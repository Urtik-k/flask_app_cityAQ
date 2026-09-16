from flask import Blueprint, render_template, request
import file_handler
url_routes = Blueprint('url_routes', __name__, template_folder='templates')

@url_routes.route('/', methods=['GET', 'POST'])
def main_page():
    if request.method == 'POST':
        city = request.form['city']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        data = file_handler.get_measurements(city, start_date=start_date, end_date=end_date)
        return render_template('index.html', city=city, start_date=start_date, end_date=end_date, data=data)
    return render_template('index.html')

@url_routes.route('/history/')
@url_routes.route('/history/<city>/<date>')
def aq_history(city=None, date=None):
    return render_template('history.html',city=city,date=date)