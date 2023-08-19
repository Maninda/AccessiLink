from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
from math import radians, sin, cos, sqrt, atan2

app = Flask(__name__)

# Enable CORS for all routes
@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*' # Replace with your frontend URL
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT'
    return response


CORS(app, methods=['GET'])  # Initialize CORS on your Flask app


# Load the car park data from the CSV file into a pandas DataFrame
car_parks_df = pd.read_csv('City_of_Perth_Car_Parks.csv')


# In-memory storage for hotel and person data
hotels = []
persons = []


# Add/edit a hotel endpoint
@app.route('/place', methods=['POST'])
def add_edit_hotel():
    data = request.get_json()
    name = data.get('name')
    longitude = data.get('longitude')
    latitude = data.get('latitude')
    availability = data.get('availability', False)
    print("a/e hotel ", name, ' longi: ', longitude, ' lat: ', latitude)

    # Update existing hotel if it already exists
    for hotel in hotels:
        if hotel['name'] == name:
            hotel['longitude'] = longitude
            hotel['latitude'] = latitude
            hotel['availability'] = availability
            return jsonify({'message': f'Updated hotel: {name}'})

    # If hotel doesn't exist, add it
    new_hotel = {
        'name': name,
        'longitude': longitude,
        'latitude': latitude,
        'availability': availability
    }
    hotels.append(new_hotel)
    find_nearest_car_parks
    return jsonify({'message': f'Added new hotel: {name}'})


def haversine_distance(lat1, lon1, lat2, lon2):
    # Convert latitude and longitude from degrees to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    # Haversine formula to calculate distance between two points on Earth
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = 6371 * c  # Radius of Earth in kilometers
    return distance


def find_nearest_car_parks(latitude, longitude, num_parks, availability):
    # Filter car parks based on availability
    print('Longitude of the person: ', longitude)
    print('Latitude of the person: ', latitude)
    print('Maximum number of search results for recommended parks: ', num_parks)
    if availability:
        available_car_parks = car_parks_df[car_parks_df['ACROD_BAYS'] > 0]
    else:
        available_car_parks = car_parks_df

    # Calculate distance for each car park
    print('Filtering for the nearby parks ...')
    available_car_parks['distance'] = available_car_parks.apply(
        lambda row: haversine_distance(latitude, longitude, row['Y'], row['X']), axis=1
    )

    # Sort by distance and select the top `num_parks` nearest car parks
    nearest_car_parks = available_car_parks.nsmallest(num_parks, 'distance')

    return nearest_car_parks[['CARPARK_NAME', 'URL']]


# Get closest car parks endpoint
@app.route('/person', methods=['GET'])
def get_closest_parks():
    data = request.args.to_dict()
    person_longitude = float(data.get('longitude'))
    person_latitude = float(data.get('latitude'))
    availability = data.get('availability').lower() == 'true'

    # Retrieve the nearest car parks
    nearest_parks = find_nearest_car_parks(person_latitude, person_longitude, num_parks=3, availability=availability)

    # Prepare the response
    closest_parks_list = []
    for index, row in nearest_parks.iterrows():
        park_info = {
            'CARPARK_NAME': row['CARPARK_NAME'],
            'URL': row['URL']
        }
        closest_parks_list.append(park_info)

    return jsonify({'closest_parks': closest_parks_list})


# Handle allocation endpoint
@app.route('/allocate', methods=['POST'])
def allocate_park():
    data = request.get_json()
    car_park_name = data.get('carParkName')
    availability = data.get('availability')
    print('Car park name to be reserved: ', car_park_name)

    # Perform allocation logic here and return a response
    # Example response for demonstration purposes
    if availability:
        update_acord_slot = int(car_parks_df[car_parks_df['CARPARK_NAME'] == car_park_name]['ACROD_BAYS'])
        print('Number of remaining ACROD parking slots before allocation: ', update_acord_slot)
        if update_acord_slot > 0:
            update_acord_slot -= 1
            success = True
            message = f'Allocation successful for {car_park_name}'
        else:
            success = False
            message = f'Allocation failed for {car_park_name}'
    else:
        success = True
        message = f'Allocation successful for {car_park_name}'
    print('Number of remaining ACROD parking slots after allocation: ', update_acord_slot)
    return jsonify({'success': success, 'message': message})


# Update hotel availability endpoint
@app.route('/person', methods=['PUT'])
def update_hotel_availability():
    data = request.get_json()
    print("hotel_availability data ", str(data))
    name = data.get('name')
    new_availability = data.get('availability')

    for hotel in hotels:
        if hotel['name'] == name:
            hotel['availability'] = new_availability
            return jsonify({'message': f'Updated availability for hotel {name}'})

    return jsonify({'error': 'Hotel not found'})


# Add/edit a person endpoint
@app.route('/person', methods=['POST'])
def add_edit_person():
    data = request.get_json()
    print("add_edit_person data ", str(data))
    name = data.get('name')
    availability = data.get('availability', False)

    # Update existing person if it already exists
    for person in persons:
        if person['name'] == name:
            person['availability'] = availability
            return jsonify({'message': f'Updated person: {name}'})

    # If person doesn't exist, add it
    new_person = {
        'name': name,
        'availability': availability
    }
    persons.append(new_person)
    return jsonify({'message': f'Added new person: {name}'})


# Get person by name endpoint
@app.route('/person/<string:name>', methods=['GET'])
def get_person_by_name(name):
    print("person_by_name ", str(name))
    for person in persons:
        if person['name'] == name:
            return jsonify(person)

    return jsonify({'error': 'Person not found'})


if __name__ == '__main__':
    app.run(debug=False, port=8080)
