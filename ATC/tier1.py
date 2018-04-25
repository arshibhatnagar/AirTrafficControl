from flask import Flask, render_template, request, jsonify
from models import Flight, FlightWaypoints
from google.appengine.ext import ndb

app = Flask(__name__)
app.debug=True

@app.route('/')
def hello_world():
    print "Hello"
    new_flight = FlightWaypoints(flight_num="AA1234", 
        next_waypoint=ndb.GeoPt(42.234, -56.345), 
        next_speed=123, next_altitude=345)
    AA1234 = ndb.Key(FlightWaypoints, "AA1234")
    new_flight.key = AA1234
    new_flight.put()
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
    fetched = flight_waypoints_key.get()
    return {"Waypoint": fetched.next_waypoint, "Speed": fetched.next_speed, "Altitude": fetched.next_altitude}

@app.route('/flight', methods=['POST'])
def incoming_flight_data():
    print "in flight"
    JSON = request.json
    flight_num = JSON.get('flight_num')
    latitude = JSON.get('latitude')
    longitude = JSON.get('longitude')
    altitude = JSON.get('altitude')
    speed = JSON.get('speed')
    temperature = JSON.get('temperature')
    flight_key = ndb.Key(Flight, flight_num)
    flight = Flight(flight_num=flight_num, location=ndb.GeoPt(latitude, longitude), 
        altitude=altitude, speed=speed, temperature=temperature)
    flight.key = flight_key

    # data = {'flight_num': "flight_num", "latitude": 43.578, "longitude": -64.341, "altitude": 123, "speed": 123, "temperature": 32.4}

    update_or_insert(flight_key, flight)
    # update_or_insert_tasklet(flight_key, flight)

    flight_waypoints_key = ndb.Key(FlightWaypoints, flight_num)
    print flight_waypoints_key.pairs()
    data = retrieve_next_data(flight_waypoints_key)

    return jsonify(data)

    # Look into using get_or_insert
    # Want to do this batched
    # Want to check cache
    # Want to communicate with tier 2 to get the data for the flight