import csv
import io
import os
import re
import unicodedata
from datetime import datetime, timedelta

from geopy.exc import GeopyError
from geopy.geocoders import Nominatim
from openaq import OpenAQ

from database import db
from models import Measurement

# Klucz API ustaw w zmiennej środowiskowej OPENAQ_API_KEY (albo w pliku .env).
# Klucz wygenerujesz na explore.openaq.org >> zakładka settings.

MAX_RESULTS = 1000          # maksymalna liczba dni pobierana z OpenAQ na jedno zapytanie
GEOCODER_TIMEOUT = 10       # sekundy (domyślne 1 s jest za krótkie)
GEOCODER_USER_AGENT = "airquality_dashboard_student_project"
PARAMETERS = ("pm25", "pm10", "no2", "co", "o3", "so2")

# CSV pod polskiego Excela: separator ";" i przecinek dziesiętny.
# Jeśli wolisz klasyczny CSV, ustaw CSV_DELIMITER = "," i CSV_DECIMAL = "."
CSV_DELIMITER = ";"
CSV_DECIMAL = ","


class DataFetchError(Exception):
    """Błąd z czytelnym komunikatem, który można pokazać użytkownikowi."""


def get_api_key():
    return os.environ.get("OPENAQ_API_KEY", "").strip()


def normalize_city(city):
    """Ujednolica nazwę miasta, żeby 'łódź', 'ŁÓDŹ' i ' Łódź ' były jednym miastem.

    - NFC: 'o' + akcent (zapis z Maca) -> pojedyncze 'ó'
    - usuwa spacje z brzegów i podwójne spacje w środku
    - pierwsza litera każdego słowa wielka, reszta mała
    """
    city = unicodedata.normalize("NFC", city or "")
    city = re.sub(r"\s+", " ", city).strip()
    return city.title()


# Litery, których Unicode nie rozkłada na "litera + akcent" (np. ł), trzeba zamienić ręcznie.
_FOLD_EXTRA = str.maketrans({"ł": "l", "Ł": "L", "ø": "o", "Ø": "O", "đ": "d", "Đ": "D"})


def fold_city(name):
    """Wersja nazwy do PORÓWNYWANIA (nie do wyświetlania): 'Łódź' -> 'lodz'."""
    name = unicodedata.normalize("NFKD", (name or "").translate(_FOLD_EXTRA))
    name = "".join(char for char in name if not unicodedata.combining(char))
    return name.casefold()


def resolve_city(city):
    """Zwraca nazwę miasta w takiej formie, jaka jest (lub będzie) zapisana w bazie.

    Jeśli w bazie jest już miasto o tej samej nazwie po spłaszczeniu
    (np. 'Łódź' dla wpisu 'lodz'), zwraca zapisaną nazwę. W przeciwnym razie
    zwraca po prostu znormalizowany wpis użytkownika.
    """
    normalized = normalize_city(city)
    if not normalized:
        return normalized

    key = fold_city(normalized)
    for (stored,) in db.session.query(Measurement.city).distinct():
        if fold_city(stored) == key:
            return stored
    return normalized


def parse_date_range(start_date, end_date):
    """Sprawdza daty z formularza. Rzuca ValueError z komunikatem po polsku."""
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d").date()
        end = datetime.strptime(end_date, "%Y-%m-%d").date()
    except (TypeError, ValueError):
        raise ValueError("Podaj poprawne daty początkową i końcową.")

    if end < start:
        raise ValueError("Data końcowa nie może być wcześniejsza niż początkowa.")
    if (end - start).days + 1 > MAX_RESULTS:
        raise ValueError(f"Zakres dat jest za duży (maksymalnie {MAX_RESULTS} dni).")
    return start, end


def find_location(city):
    geolocator = Nominatim(user_agent=GEOCODER_USER_AGENT, timeout=GEOCODER_TIMEOUT)
    try:
        location = geolocator.geocode(city, language="pl")
    except GeopyError:
        raise DataFetchError(
            "Usługa wyszukiwania miast nie odpowiada. Spróbuj ponownie za chwilę."
        )
    if location is None:
        raise DataFetchError(f"Nie znaleziono miasta „{city}”. Sprawdź pisownię.")


    official_name = location.raw.get("name") or city
    return (location.latitude, location.longitude), normalize_city(official_name)


def get_sensors(api_client, coordinates):
    locations = api_client.locations.list(
        coordinates=coordinates, radius=10000, monitor=True
    )
    locations.results.sort(key=lambda location: location.distance)

    available_parameters = {}

    for location in locations.results:
        for sensor in location.sensors:
            parameter = sensor.parameter.name

            if parameter not in available_parameters:
                available_parameters[parameter] = []
            available_parameters[parameter].append({
                "sensor_id": sensor.id,
                "location_id": location.id,
                "location_name": location.name,
                "distance": location.distance,
                "unit": sensor.parameter.units
            })

    return available_parameters


def get_measurements(city, start_date, end_date):
    if not get_api_key():
        raise DataFetchError(
            "Brak klucza API OpenAQ. Ustaw zmienną OPENAQ_API_KEY (patrz README)."
        )

    coordinates, official_name = find_location(city)

    api_client = OpenAQ(api_key=get_api_key())
    measurements = {}

    try:
        sensors = get_sensors(api_client, coordinates)

        for parameter, sensor_list in sensors.items():
            for sensor_data in sensor_list:
                result = api_client.measurements.list(
                    sensors_id=sensor_data["sensor_id"],
                    data="days",
                    date_from=start_date,
                    date_to=end_date,
                    limit=MAX_RESULTS
                )

                if result.results:
                    measurements[parameter] = {
                        "results": result.results,
                        "location_name": sensor_data["location_name"],
                        "distance": sensor_data["distance"],
                        "unit": sensor_data["unit"]
                    }
                    break
    except DataFetchError:
        raise
    except Exception as error:
        raise DataFetchError(
            "Nie udało się pobrać danych z OpenAQ "
            f"({type(error).__name__}). Sprawdź klucz API i połączenie z internetem."
        )
    finally:
        api_client.close()

    return measurements, official_name


def prepare_table_data(measurements, start=None, end=None):
    """Zamienia odpowiedź API na {data: {parametr: wartość}}.

    Jeśli podano start/end (obiekty date), odrzuca dni spoza zakresu.
    """
    table_data = {}

    for parameter, parameter_data in measurements.items():
        for measurement in parameter_data["results"]:
            measurement_date = measurement.period.datetime_from.local[:10]

            if start and end:
                day = datetime.strptime(measurement_date, "%Y-%m-%d").date()
                if day < start or day > end:
                    continue

            if measurement_date not in table_data:
                table_data[measurement_date] = {}

            table_data[measurement_date][parameter] = measurement.value
    return table_data


def get_dates_range(start_date, end_date):
    start = datetime.strptime(start_date, "%Y-%m-%d").date()
    end = datetime.strptime(end_date, "%Y-%m-%d").date()

    dates = []

    current_date = start
    while current_date <= end:
        dates.append(current_date)
        current_date += timedelta(days=1)

    return dates


def search_db(city, start_date, end_date):
    city = normalize_city(city)
    requested_dates = get_dates_range(start_date, end_date)

    db_records = Measurement.query.filter(
        Measurement.city == city,
        Measurement.date >= requested_dates[0],
        Measurement.date <= requested_dates[-1]
    ).all()

    available_dates = {record.date for record in db_records}

    return [date for date in requested_dates if date not in available_dates]


def get_from_db(city, start_date=None, end_date=None):
    city = normalize_city(city)

    query = Measurement.query.filter(Measurement.city == city)

    if start_date and end_date:
        start = datetime.strptime(start_date, "%Y-%m-%d").date()
        end = datetime.strptime(end_date, "%Y-%m-%d").date()

        query = query.filter(
            Measurement.date >= start,
            Measurement.date <= end
        )

    records = query.order_by(Measurement.date, Measurement.id).all()

    table_data = {}

    for record in records:
        date = record.date.strftime("%Y-%m-%d")
        entry = table_data.setdefault(date, {})

        # Gdyby w bazie były stare duplikaty tego samego dnia, łączymy je:
        # puste wartości nie nadpisują tych, które już mamy.
        for parameter in PARAMETERS:
            value = getattr(record, parameter)
            if value is not None or parameter not in entry:
                entry[parameter] = value

    return table_data


def save_to_db(city, data):
    """Zapisuje pomiary. Istniejący wpis (miasto + data) jest uzupełniany, a nie dublowany."""
    if not data:
        return

    city = normalize_city(city)
    parsed = {
        datetime.strptime(date_string, "%Y-%m-%d").date(): parameters
        for date_string, parameters in data.items()
    }

    existing_rows = Measurement.query.filter(
        Measurement.city == city,
        Measurement.date >= min(parsed),
        Measurement.date <= max(parsed)
    ).all()
    existing = {row.date: row for row in existing_rows}

    for measurement_date, parameters in parsed.items():
        row = existing.get(measurement_date)
        if row is None:
            row = Measurement(city=city, date=measurement_date)
            db.session.add(row)

        for parameter in PARAMETERS:
            if parameters.get(parameter) is not None:
                setattr(row, parameter, parameters[parameter])

    db.session.commit()


def _csv_value(value):
    if value is None:
        return ""
    return str(value).replace(".", CSV_DECIMAL)


def data_to_csv(data):
    output = io.StringIO()
    writer = csv.writer(output, delimiter=CSV_DELIMITER)

    writer.writerow(["date", *PARAMETERS])

    for date, measurement in sorted(data.items()):
        writer.writerow([date, *(_csv_value(measurement.get(p)) for p in PARAMETERS)])

    return output.getvalue()
