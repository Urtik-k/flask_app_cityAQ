import re
import unicodedata
from urllib.parse import quote

from flask import Blueprint, Response, current_app, render_template, request

import file_handler
from database import db
from models import Measurement


url_routes = Blueprint('url_routes', __name__,
                       template_folder='templates',
                       static_folder='static')

_PL_TO_ASCII = str.maketrans("ĄĆĘŁŃÓŚŹŻąćęłńóśźż", "ACELNOSZZacelnoszz")


def _ascii_filename(name):
    """Zapasowa nazwa pliku dla starszych przeglądarek (bez polskich znaków)."""
    name = name.translate(_PL_TO_ASCII)
    name = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    return re.sub(r"[^A-Za-z0-9._-]", "_", name)


def _form_error(message, city, start_date, end_date, status):
    """Pokazuje formularz z komunikatem, zachowując to, co użytkownik wpisał."""
    return render_template('index.html', error=message, city=city,
                           start_date=start_date, end_date=end_date), status


@url_routes.route('/', methods=['GET', 'POST'])
def main_page():
    if request.method == 'GET':
        return render_template('index.html')

    raw_city = request.form.get('city', '').strip()
    start_date = request.form.get('start_date', '').strip()
    end_date = request.form.get('end_date', '').strip()

    city = file_handler.resolve_city(raw_city)
    if not city:
        return _form_error("Wpisz nazwę miasta.", raw_city, start_date, end_date, 400)

    try:
        start, end = file_handler.parse_date_range(start_date, end_date)
    except ValueError as error:
        return _form_error(str(error), raw_city, start_date, end_date, 400)

    warning = None

    try:
        missing_dates = file_handler.search_db(city, start_date, end_date)
        db_data = file_handler.get_from_db(city, start_date, end_date)

        if missing_dates:
            try:
                api_data, official_name = file_handler.get_measurements(
                    city, str(min(missing_dates)), str(max(missing_dates)))
                # Zapisujemy pod oficjalną nazwą (lub pod już istniejącą w bazie).
                city = file_handler.resolve_city(official_name)
                new_data = file_handler.prepare_table_data(api_data, start, end)
                file_handler.save_to_db(city, new_data)
                db_data = file_handler.get_from_db(city, start_date, end_date)
            except file_handler.DataFetchError as error:
                warning = str(error)
    except Exception:
        db.session.rollback()
        current_app.logger.exception("Błąd podczas obsługi wyszukiwania")
        return _form_error("Wystąpił nieoczekiwany błąd. Spróbuj ponownie.",
                           raw_city, start_date, end_date, 500)

    # Problem z pobieraniem danych z API i pusta baza db
    if warning and not db_data:
        return _form_error(warning, raw_city, start_date, end_date, 502)

    return render_template('history.html',
                           city=city,
                           start_date=start_date,
                           end_date=end_date,
                           data=db_data,
                           warning=warning)


@url_routes.route('/history/')
@url_routes.route('/history/<city>/')
def aq_history(city=None):

    if city is None:
        cities = db.session.query(
            Measurement.city
        ).distinct().order_by(Measurement.city).all()

        cities = [item[0] for item in cities]

        return render_template(
            'history.html',
            cities=cities,
            city=None,
            data=None
        )

    city = file_handler.resolve_city(city)
    data = file_handler.get_from_db(city, None, None)

    return render_template(
        'history.html',
        cities=None,
        city=city,
        data=data
    )


@url_routes.route('/download/<city>')
def download(city):
    city = file_handler.resolve_city(city)
    data = file_handler.get_from_db(city)

    if not data:
        return "Brak danych do pobrania", 404

    csv_data = file_handler.data_to_csv(data)
    filename = f"air_quality_{city}.csv"

    return Response(
        "\ufeff" + csv_data,   # BOM, żeby Excel poprawnie wczytał polskie znaki
        content_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": (
                f'attachment; filename="{_ascii_filename(filename)}"; '
                f"filename*=UTF-8''{quote(filename)}"
            )
        }
    )


@url_routes.route('/delete/<int:pid>',methods=['DELETE'])
def delete(pid):
    measurement_to_delete = db.session.get(Measurement, pid)

    if measurement_to_delete is None:
        return "Nie znaleziono wyniku", 404

    try:
        db.session.delete(measurement_to_delete)
        db.session.commit()
    except Exception:
        db.session.rollback()
        current_app.logger.exception("Błąd podczas usuwania wyniku")
        return "Problem z usuwaniem wyniku", 500

    return "", 204

