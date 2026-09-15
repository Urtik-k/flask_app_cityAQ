from openaq import OpenAQ
from geopy.geocoders import Nominatim

####### TU WRZUĆ SWÓJ API KEY Z explore.openaq.org >> zakładka settings
API_KEY = ""

def find_location(city):
    geolocator = Nominatim(user_agent="coordinates_finder")
    place = geolocator.geocode(city.capitalize())
    if place is None:
        return None
    return place.latitude, place.longitude


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
                available_parameters[parameter] = {
                    "sensor_id": sensor.id,
                    "location_id": location.id,
                    "location_name": location.name,
                    "distance": location.distance,
                    "unit": sensor.parameter.units
                }

    api_client.close()
    return available_parameters

def get_measurements(city,start_date,end_date):
    api_client = OpenAQ(api_key=API_KEY)
    sensors = get_sensors(city)
    if sensors is None:
        api_client.close()
        return None

    measurements = {}
    for parameter, sensor_data in sensors.items():
        sensor_id = sensor_data["sensor_id"]
        result = api_client.measurements.list(sensors_id=sensor_id, data="days", date_from=start_date, date_to=end_date, limit=100)
        print(parameter)
        print(result.results)
        measurements[parameter] = result
    api_client.close()
    return measurements

print(get_measurements("kraków","2026-09-10","2026-09-12"))
# import urllib
#
# import requests
# from geopy.geocoders import Nominatim
#
# #TU WSTAW SWÓJ API_KEY Z explore.openaq.org >> zakładka settings
# API_KEY =""
#
# def find_location(city):
#     city = city.capitalize()
#     geolocator = Nominatim(user_agent="coords_finder")
#     location = geolocator.geocode(city)
#     if location is None:
#         return None
#     latitude = location.latitude
#     longitude = location.longitude
#     return f"{latitude},{longitude}"
#
#
# def get_data_from_api(city):
#     coordinates = find_location(city)
#     url = "https://api.openaq.org/v3/parameters/2/"
#     headers = {"X-Api-Key": API_KEY}
#     params = {
#         "coordinates": coordinates,
#         "radius": 25000,
#         "limit": 5
#     }
#     response = requests.get(url, headers=headers, params=params)
#     print(response)
#     if response.status_code == 200:
#         return response.json()
#     else:
#         return None
#
#
# def get_air_quality(city,date=None):
#
#     data = get_data_from_api(city)
#     return data
#
# print(get_data_from_api("Wrocław"))