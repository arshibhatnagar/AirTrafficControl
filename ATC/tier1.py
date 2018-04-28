from flask import Flask, render_template, request, jsonify
from models import Flight, FlightWaypoints, FlightPlan, Route
from google.appengine.ext import ndb
import datetime

app = Flask(__name__)
app.debug=True

@app.route('/')
def hello_world():
    # print "Hello"
    # new_flight = FlightWaypoints(
    #     flight_num="AA1234", next_waypoint=ndb.GeoPt(42.234, -56.345), 
    #     next_speed=123, next_altitude=345)
    # AA1234 = ndb.Key(FlightWaypoints, "AA1234")
    # print "flight waypoints key is: "
    # print AA1234
    # new_flight.key = AA1234
    # flight_waypoint_key = new_flight.put()
    return 'Hello, World! This is a test!' # + flight_waypoint_key.urlsafe()

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

def update_or_insert_flight(flight, flight_key_urlsafe):
    if flight_key_urlsafe is not None:
        flight_key = ndb.Key(urlsafe=flight_key_urlsafe)
        fetched = flight_key.get()
        fetched.location = flight.location
        fetched.altitude = flight.altitude
        fetched.speed = flight.speed
        fetched.temperature = flight.temperature
        return fetched.put()
    else:
        return flight.put()

def insert_flight_waypoints(flight_num, flight_key_urlsafe):
    INITIAL_SPEED = 200
    INITIAL_ALTITUDE = 500
    flight_plan = FlightPlan.query(FlightPlan.flight_num == flight_num).fetch(1)[0]
    first_waypoint = flight_plan.current_route.waypoints[0]
    new_flight_waypoints = FlightWaypoints(flight_num=flight_num, next_waypoint=first_waypoint, 
        next_speed=INITIAL_SPEED, next_altitude=INITIAL_ALTITUDE, flight_plan_urlsafe=flight_plan.key.urlsafe(), 
        flight_urlsafe=flight_key_urlsafe, current_route_index=0)
    data = {"Waypoint": [first_waypoint.lat, first_waypoint.lon], "Speed": INITIAL_SPEED, "Altitude": INITIAL_ALTITUDE}
    return (new_flight_waypoints.put(), data)

def retrieve_next_data(flight_waypoints_key_urlsafe):
    flight_waypoints_key = ndb.Key(urlsafe=flight_waypoints_key_urlsafe)
    fetched = flight_waypoints_key.get()
    return {"Waypoint": [fetched.next_waypoint.lat, fetched.next_waypoint.lon], "Speed": fetched.next_speed, "Altitude": fetched.next_altitude}

@app.route('/flight', methods=['POST'])
def incoming_flight_data():
    JSON = request.json
    flight_num = JSON.get('flight_num')
    latitude = JSON.get('latitude')
    longitude = JSON.get('longitude')
    altitude = JSON.get('altitude')
    speed = JSON.get('speed')
    temperature = JSON.get('temperature')
    flight_key_urlsafe = JSON.get('flight_key_urlsafe') if 'flight_key_urlsafe' in JSON else None
    flight_waypoints_key_urlsafe = JSON.get('flight_waypoints_key_urlsafe') if 'flight_waypoints_key_urlsafe' in JSON else None
        
    flight = Flight(flight_num=flight_num, location=ndb.GeoPt(latitude, longitude), 
        altitude=altitude, speed=speed, temperature=temperature)
    flight_key = update_or_insert_flight(flight, flight_key_urlsafe)

    if (flight_waypoints_key_urlsafe is None):
        flight_waypoints_key, data = insert_flight_waypoints(flight_num, flight_key.urlsafe())
        data['flight_waypoints_key_urlsafe'] = flight_waypoints_key.urlsafe()
    else:
        data = retrieve_next_data(flight_waypoints_key_urlsafe)
    
    if flight_key_urlsafe is None:
        flight_key_urlsafe_to_send = flight_key.urlsafe()
        data['flight_key_urlsafe'] = flight_key_urlsafe_to_send

    return jsonify(data)

    # Look into using get_or_insert
    # Want to do this batched
    # Want to check cache
    # Want to communicate with tier 2 to get the data for the flight

@app.route('/insert_flight_plan', methods=['POST'])
def insert_flight_plan():
    JSON = request.json
    flight_num = JSON.get('flight_num')
    origin = JSON.get('origin')
    dest = JSON.get('dest')
    cancelled = False 
    carrier = JSON.get('carrier')

    departure_date = JSON.get('dep_date').split('/')
    departure_time = JSON.get('dep_time').split(':')
    dep_time = datetime.datetime(int(departure_date[0]), int(departure_date[1]), int(departure_date[2]), int(departure_time[0]), int(departure_time[1]))

    arrival_date = JSON.get('arr_date').split('/')
    arrival_time = JSON.get('arr_time').split(':')
    arr_time = datetime.datetime(int(arrival_date[0]), int(arrival_date[1]), int(arrival_date[2]), int(arrival_time[0]), int(arrival_time[1]))

    route = JSON.get('current_route')
    current_route = []
    for waypoint in route:
        current_route.append(ndb.GeoPt(waypoint[0], waypoint[1]))

    flight_plan = FlightPlan(flight_num=flight_num, origin=origin, dest=dest, dep_time=dep_time, 
        arr_time=arr_time, cancelled=cancelled, carrier=carrier, current_route=Route(waypoints=current_route))
    return flight_plan.put().urlsafe()

