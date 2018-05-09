# IN THE YAML FILE, SET INSTANCE CLASS TO INSTANCES WITH BIGGER MEMORY AND A FIXED NUMBER OF RUNNING INSTANCES
from flask import Flask, render_template, request, jsonify
from models import Flight, FlightWaypoints, FlightPlan, Route
from google.appengine.ext import ndb
import datetime
import requests
import requests_toolbelt.adapters.appengine
import json
from google.appengine.api import memcache, taskqueue

requests_toolbelt.adapters.appengine.monkeypatch()

''' 

Introduced async stuff into tier 1. Created a bunch of tasklets to essentially constantly look for info in
datastore, then yield to other tasklets so all the operations become asyncronous, and no reliability
upon one another. Still need to test and make sure the tasklets have no interdependencies on them, otherwise
it's more suitable to make the appropriate parts syncronous.

'''

app = Flask(__name__)
app.debug=True

MAX_VERSION_DIFFERENCE = 6
MIN_REPLICATED_UPDATE_DIFFERENCE = 6
INITIAL_SPEED = 200.0
INITIAL_ALTITUDE = 500.0

client = memcache.Client()


@ndb.toplevel
@ndb.tasklet
def update_or_insert_tasklet(flight_key_urlsafe, flight):
    if flight_key_urlsafe is not None:
        flight_key = ndb.Key(urlsafe=flight_key_urlsafe)
        fetched = yield flight_key.get_async()
        fetched.location = flight.location
        fetched.altitude = flight.altitude
        fetched.speed = flight.speed
        fetched.temperature = flight.temperature
        fetched.version += 1
        fetched_key = yield fetched.put_async()
        raise ndb.Return(fetched_key)
    else:
        flight_key = yield flight.put_async()
        raise ndb.Return(flight_key)


@ndb.toplevel
@ndb.tasklet
def insert_flight_waypoints_tasklet(flight_num, flight_key_urlsafe):

    flight_plans =  yield FlightPlan.query(FlightPlan.flight_num == flight_num).fetch_async(1)
    flight_plan = flight_plans[0]
    first_waypoint = flight_plan.current_route.waypoints[0]
    new_flight_waypoints = FlightWaypoints(flight_num=flight_num, next_waypoint=first_waypoint, 
        next_speed=INITIAL_SPEED, next_altitude=INITIAL_ALTITUDE, flight_plan_urlsafe=flight_plan.key.urlsafe(), 
        flight_urlsafe=flight_key_urlsafe, current_route_index=0, version=0)
    data = {"Waypoint": [first_waypoint.lat, first_waypoint.lon], "Speed": INITIAL_SPEED, "Altitude": INITIAL_ALTITUDE}
    flight_waypoints = yield new_flight_waypoints.put_async()
    raise ndb.Return((flight_waypoints, data)) 


@ndb.toplevel
@ndb.tasklet
def retrieve_next_data_tasklet(flight_waypoints_key_urlsafe, flight_key_urlsafe):
    flight_key = ndb.Key(urlsafe=flight_key_urlsafe)
    fetched = client.get(flight_key_urlsafe)
    
    if fetched is None:
        print "MISS"
        flight_waypoints_key = ndb.Key(urlsafe=flight_waypoints_key_urlsafe)
        fetched, flight = yield flight_waypoints_key.get_async(), flight_key.get_async()
    else:
        flight = yield flight_key.get_async()
    if flight.version - fetched.version < MAX_VERSION_DIFFERENCE:
        raise ndb.Return({"Waypoint": [fetched.next_waypoint.lat, fetched.next_waypoint.lon], "Speed": fetched.next_speed, "Altitude": fetched.next_altitude})
    else:
        response = requests.post('http://localhost:8081/specific_waypoint_update', 
            json={"flight_waypoints_key_urlsafe": flight_waypoints_key_urlsafe, "flight_key_urlsafe": flight_key_urlsafe}).content
        raise ndb.Return(json.loads(response))


@ndb.toplevel
@ndb.synctasklet
def input_flight_data(JSON):
    flight_num = JSON.get('flight_num')
    latitude = JSON.get('latitude')
    longitude = JSON.get('longitude')
    altitude = JSON.get('altitude')
    speed = JSON.get('speed')
    temperature = JSON.get('temperature')
    flight_key_urlsafe = JSON.get('flight_key_urlsafe') if 'flight_key_urlsafe' in JSON else None
    flight_waypoints_key_urlsafe = JSON.get('flight_waypoints_key_urlsafe') if 'flight_waypoints_key_urlsafe' in JSON else None
        
    flight = Flight(flight_num=flight_num, location=ndb.GeoPt(latitude, longitude), 
        altitude=altitude, speed=speed, temperature=temperature, version=0)

    if (flight_waypoints_key_urlsafe is None):
        flight_key = yield update_or_insert_tasklet(flight_key_urlsafe, flight)
        flight_waypoints_key, data = yield insert_flight_waypoints_tasklet(flight_num, flight_key.urlsafe())
        data['flight_waypoints_key_urlsafe'] = flight_waypoints_key.urlsafe()
    else:
        flight_key, data = yield update_or_insert_tasklet(flight_key_urlsafe, flight), retrieve_next_data_tasklet(flight_waypoints_key_urlsafe, flight_key_urlsafe)
    
    if flight_key_urlsafe is None:
        flight_key_urlsafe_to_send = flight_key.urlsafe()
        data['flight_key_urlsafe'] = flight_key_urlsafe_to_send

    output = jsonify(data)
    raise ndb.Return(output)


@ndb.toplevel
@ndb.synctasklet
def flight_plan_insert(JSON):
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
    flight_plan_key = yield flight_plan.put_async()
    raise ndb.Return(flight_plan_key.urlsafe())


@ndb.toplevel
@ndb.synctasklet
def check_update_done(flight_key_urlsafe, flight):
    flight_key = ndb.Key(urlsafe=flight_key_urlsafe)
    fetched = yield flight_key.get_async()
    if ((datetime.datetime.now() - fetched.last_updated).total_seconds() > MIN_REPLICATED_UPDATE_DIFFERENCE):
        fetched.location = flight.location
        fetched.altitude = flight.altitude
        fetched.speed = flight.speed
        fetched.temperature = flight.temperature
        fetched.version += 1
        fetched_key = yield fetched.put_async()
        raise ndb.Return(True)
    else:
        raise ndb.Return(False)


@app.route('/flight', methods=['POST'])
def incoming_flight_data():
    task = taskqueue.add(
            url='/flight',
            method='POST',
            headers={'Content-Type': 'application/json'},
            payload=json.dumps(request.json),
            countdown=6)
    JSON = request.json
    output = input_flight_data(JSON)
    deleted = taskqueue.Queue('default').delete_tasks(task)
    return output


@app.route('/insert_flight_plan', methods=['POST'])
def insert_flight_plan():
    JSON = request.json
    flight_plan_key_urlsafe = flight_plan_insert(JSON)
    return flight_plan_key_urlsafe

@app.route('/replicate_request', methods=['POST'])
def replicate_request():
    JSON = request.json
    flight_num = JSON.get('flight_num')
    latitude = JSON.get('latitude')
    longitude = JSON.get('longitude')
    altitude = JSON.get('altitude')
    speed = JSON.get('speed')
    temperature = JSON.get('temperature')
    flight_key_urlsafe = JSON.get('flight_key_urlsafe') if 'flight_key_urlsafe' in JSON else None

    flight = Flight(flight_num=flight_num, location=ndb.GeoPt(latitude, longitude), 
        altitude=altitude, speed=speed, temperature=temperature, version=0)

    if flight_key_urlsafe is None:
        return "FLIGHT KEY DOES NOT EXIST. NOT INSERTED YET."

    else:
        updated = check_update_done(flight_key_urlsafe, flight)
        if updated:
            return "REPLICATED REQUEST UPDATED"

    return "NO NEED TO REPLICATE"



@app.route('/')
def hello_world():
    return 'Hello, World! This is a test!'

