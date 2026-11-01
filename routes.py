from flask import Blueprint, render_template, request
from datetime import datetime, timedelta
import file_handler
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
            print(f'missing_dates found')
            api_data = file_handler.get_measurements(city,
                                                     str(min(missing_dates)),
                                                     str(max(missing_dates)))
            if api_data:
                new_data = file_handler.prepare_table_data(api_data)
                file_handler.save_to_db(city, new_data)
                print(f'SAVING TO DB {city} : {new_data}')

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
@url_routes.route('/history/<city>/<start_date>/<end_date>')
def aq_history(city=None, start_date=None, end_date=None):
    measurements = Measurement.query.all()
    return str(measurements)
    # return render_template('history.html',city=city,start_date=start_date,end_date=end_date)

