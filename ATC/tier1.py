from flask import Flask, render_template, request, jsonify
from models import Flight, FlightWaypoints
from google.appengine.ext import ndb

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World! This is a test!'

@ndb.toplevel
@ndb.synctasklet
def update_or_insert_tasklet(flight_key, flight):
    fetched = yield flight_key.get_async()
    if fetched is not None:
        fetched.latitude = flight.latitude
        fetched.longitude = flight.longitude
        fetched.altitude = flight.altitude
        fetched.speed = flight.speed
        fetched.temperature = flight.temperature
        yield fetched.put_async()
    else:
        yield flight.put_async()
    # return True

@ndb.toplevel
def update_or_insert_async(flight_key, flight):
    fetched_future = flight_key.get_async()
    fetched = fetched_future.get_result()
    if fetched is not None:
        fetched.latitude = flight.latitude
        fetched.longitude = flight.longitude
        fetched.altitude = flight.altitude
        fetched.speed = flight.speed
        fetched.temperature = flight.temperature
        fetched.put_async() # does this have to be async
    else:
        flight.put_async() # does this have to be async

def update_or_insert(flight_key, flight):
    fetched = flight_key.get()
    if fetched is not None:
        fetched.latitude = flight.latitude
        fetched.longitude = flight.longitude
        fetched.altitude = flight.altitude
        fetched.speed = flight.speed
        fetched.temperature = flight.temperature
        fetched.put()
    else:
        flight.put()

def retrieve_next_data(flight_waypoints_key):
    fetched = flight_key.get()
    return {"Waypoint": fetched.next_waypoint, "Speed": fetched.next_speed, "Altitude": fetched.next_altitude}

@app.route('/flight', methods=['POST'])
def incoming_flight_data():
    JSON = request.json
    flight_num = JSON.get('flight_num')
    latitude = JSON.get('latitude')
    longitude = JSON.get('longitude')
    altitude = JSON.get('altitude')
    speed = JSON.get('speed')
    temperature = JSON.get('temperature')
    flight_key = ndb.Key(Flight, flight_num)
    flight = Flight(flight_num=flight_num, latitude=latitude, longitude=longitude, 
        altitude=altitude, speed=speed, temperature=temperature)
    flight.key = flight_key

    update_or_insert(flight_key, flight)
    # update_or_insert_tasklet(flight_key, flight)

    flight_waypoints_key = ndb.Key(FlightWaypoints, flight_num)
    data = retrieve_next_data(flight_waypoints_key)

    return jsonify(data)

    # Look into using get_or_insert
    # Want to do this batched
    # Want to check cache
    # Want to communicate with tier 2 to get the data for the flight