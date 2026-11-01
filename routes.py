from flask import Blueprint, render_template, request, Response
import file_handler
from database import db
from models import Measurement
url_routes = Blueprint('url_routes', __name__,
                       template_folder='templates',
                       static_folder='static')

@url_routes.route('/', methods=['GET', 'POST'])
def main_page():
    if request.method == 'POST':
        city = request.form['city']
        start_date = request.form['start_date']
        end_date = request.form['end_date']

        missing_dates = file_handler.search_db(city, start_date, end_date)

        db_data = file_handler.get_from_db(city, start_date, end_date)

        if missing_dates:
            api_data = file_handler.get_measurements(city,
                                                     str(min(missing_dates)),
                                                     str(max(missing_dates)))
            if api_data:
                new_data = file_handler.prepare_table_data(api_data)
                file_handler.save_to_db(city, new_data)

                for date, parameters in new_data.items():
                    if date not in db_data:
                        db_data[date] = {}
                    db_data[date].update(parameters)
        return render_template('history.html',
                               city=city,
                               start_date=start_date,
                               end_date=end_date,
                               data=db_data)

    return render_template('index.html')

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

    data = file_handler.get_from_db(city, None, None)

    return render_template(
        'history.html',
        cities=None,
        city=city,
        data=data
    )


@url_routes.route('/download<city>')
def download(city):
    data = file_handler.get_from_db(city)

    if not data:
        return "brak danych do pobrania", 404

    csv_data = file_handler.data_to_csv(data)
    return Response(
        "\ufeff" + csv_data,
        mimetype='text/csv; charset=utf-8',
        headers={'Content-Disposition':
                     f'attachment; filename="air_quality_{city}.csv"'
                 }
    )

