from openaq import OpenAQ
from geopy.geocoders import Nominatim
from database import db
from models import Measurement
from datetime import datetime, timedelta

################## TU WRZUĆ SWÓJ API KEY Z explore.openaq.org >> zakładka settings ###################################
API_KEY = "6f39f8046b63a80367cb92314214d2d03bbb7aeefe512c034262e81a3df2e561"

def find_location(city):
    geolocator = Nominatim(user_agent="coordinates_finder")
    coordinates = geolocator.geocode(city.capitalize())
    if coordinates is None:
        return None
    return coordinates.latitude, coordinates.longitude


def get_sensors(city):
    api_client = OpenAQ(api_key=API_KEY)
    coordinates = find_location(city)
    if coordinates is None:
        api_client.close()
        return None

    locations = api_client.locations.list(coordinates=coordinates, radius=10000, monitor=True)
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

    api_client.close()
    return available_parameters

def get_measurements(city, start_date, end_date):
    api_client = OpenAQ(api_key=API_KEY)

    sensors = get_sensors(city)
    if sensors is None:
        api_client.close()
        return None

    measurements = {}

    for parameter, sensor_list in sensors.items():

        for sensor_data in sensor_list:
            sensor_id = sensor_data["sensor_id"]

            result = api_client.measurements.list(
                sensors_id=sensor_id,
                data="days",
                date_from=start_date,
                date_to=end_date,
                limit=100
            )

            if result.results:
                measurements[parameter] = {
                    "results": result.results,
                    "location_name": sensor_data["location_name"],
                    "distance": sensor_data["distance"],
                    "unit": sensor_data["unit"]
                }
                break

    api_client.close()
    return measurements

def prepare_table_data(measurements):

    table_data = {}

    for parameter, parameter_data in measurements.items():
        for measurement in parameter_data["results"]:
            measurement_date = measurement.period.datetime_from.local[:10]

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


def search_db(city,start_date,end_date):
    requested_dates = get_dates_range(start_date, end_date)

    print("REQUESTED DATES:", requested_dates)

    db_records = Measurement.query.filter(
        Measurement.city == city,
        Measurement.date >= requested_dates[0],
        Measurement.date <= requested_dates[-1]
    ).all()

    print("DB RECORDS:", db_records)

    available_dates = {
        record.date for record in db_records
    }

    print("AVAILABLE DATES:", available_dates)


    missing_dates = [
        date for date in requested_dates if date not in available_dates
    ]

    print("MISSING DATES:", missing_dates)

    return missing_dates

def get_from_db(city,start_date,end_date):

    start = datetime.strptime(start_date, "%Y-%m-%d").date()
    end = datetime.strptime(end_date, "%Y-%m-%d").date()

    records = Measurement.query.filter(
        Measurement.city == city,
        Measurement.date >= start,
        Measurement.date <= end
    ).all()

    table_data = {}

    for record in records:
        date = record.date.strftime("%Y-%m-%d")

        table_data[date] = {
            "pm25": record.pm25,
            "pm10": record.pm10,
            "no2": record.no2,
            "co": record.co,
            "o3": record.o3,
            "so2": record.so2
        }

    return table_data

def save_to_db(city,data):

    for date_string, parameters in data.items():

        measurement_date = datetime.strptime(
            date_string,
            "%Y-%m-%d"
        ).date()

        new_measurement = Measurement(
            city=city,
            date=measurement_date,
            pm25=parameters.get("pm25"),
            pm10=parameters.get("pm10"),
            no2=parameters.get("no2"),
            co=parameters.get("co"),
            o3=parameters.get("o3"),
            so2=parameters.get("so2")
        )

        db.session.add(new_measurement)

    db.session.commit()