from openaq import OpenAQ
from geopy.geocoders import Nominatim

################## TU WRZUĆ SWÓJ API KEY Z explore.openaq.org >> zakładka settings ###################################
API_KEY = ""

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