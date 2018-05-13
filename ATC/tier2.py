# IN THE YAML FILE, SET INSTANCE CLASS TO INSTANCES WITH BIGGER MEMORY AND A FIXED NUMBER OF RUNNING INSTANCES
from flask import Flask, render_template, request, jsonify
from models import Flight, FlightPlan, FlightWaypoints
from google.appengine.ext import ndb
from google.appengine.api import memcache, taskqueue

app = Flask(__name__)
app.debug=True

client = memcache.Client()


@ndb.toplevel
@ndb.synctasklet
def execute_updates():
    waypoints_qry = FlightWaypoints.query().order(FlightWaypoints.version)
    # Can use the map function for tasklets. Look into that.
    results = yield waypoints_qry.fetch_async()
    # last_page = False
    # if not more:
    #     last_page = True
    # while (more or last_page):
    #     if (last_page):
    #         last_page = False
    #     if more:
    #         next_results, next_cursor, next_more = yield waypoints_qry.fetch_page_async(page_size=10, start_cursor=cursor)
    #         if (not next_more):
    #             last_page = True

    flight_plan_keys = [ndb.Key(urlsafe=flight.flight_plan_urlsafe) for flight in results]
    flight_keys = [ndb.Key(urlsafe=flight.flight_urlsafe) for flight in results]
    flight_plans, flights = yield ndb.get_multi_async(flight_plan_keys), ndb.get_multi_async(flight_keys)
    new_flight_parameters = [flight.location for flight in flights]

    to_cache = {}

    for i in range(len(results)):
        flight_waypoints = results[i]
        flight = flights[i]
        flight_plan = flight_plans[i]

        new_parameters = {'next_waypoint': flight_waypoints.next_waypoint, 'next_altitude': 5000.0, 'next_speed': 975.0}
        if ((flight.location.lat- flight_waypoints.next_waypoint.lat)**2 + (flight.location.lon - flight_waypoints.next_waypoint.lon)**2)**0.5 < 0.1:
            if (flight_waypoints.current_route_index < len(flight_plan.current_route.waypoints) - 1):
                new_parameters['next_waypoint'] = flight_plan.current_route.waypoints[flight_waypoints.current_route_index + 1]
                flight_waypoints.current_route_index += 1

        flight_waypoints.next_waypoint = new_parameters['next_waypoint']
        flight_waypoints.next_altitude = new_parameters['next_altitude']
        flight_waypoints.next_speed = new_parameters['next_speed']
        flight_waypoints.version = flight.version

        client.set(flight_waypoints.flight_urlsafe, flight_waypoints)

            # to_cache[flight_waypoints.flight_urlsafe] = flight_waypoints

    yield ndb.put_multi_async(results)
        # print client.set_multi(to_cache)

        # if more:
        #     results = next_results
        #     cursor = next_cursor
        #     more = next_more
    task = taskqueue.add(
            queue_name='backend',
            url='/waypoint_updates',
            method='GET')
    raise ndb.Return(True)

@ndb.toplevel
@ndb.synctasklet
def execute_waypoint_update(flight_waypoints_key, flight_key):
    flight_waypoints, flight = yield flight_waypoints_key.get_async(), flight_key.get_async()
    flight_plan = yield ndb.Key(urlsafe=flight_waypoints.flight_plan_urlsafe).get_async()
    new_parameters = {'next_waypoint': flight_waypoints.next_waypoint, 'next_altitude': 5000.0, 'next_speed': 975.0}
    if ((flight.location.lat- flight_waypoints.next_waypoint.lat)**2 + (flight.location.lon - flight_waypoints.next_waypoint.lon)**2)**0.5 < 0.1:
        if (flight_waypoints.current_route_index < len(flight_plan.current_route.waypoints) - 1):
            new_parameters['next_waypoint'] = flight_plan.current_route.waypoints[flight_waypoints.current_route_index + 1]
            flight_waypoints.current_route_index += 1
    flight_waypoints.next_waypoint = new_parameters['next_waypoint']
    flight_waypoints.next_altitude = new_parameters['next_altitude']
    flight_waypoints.next_speed = new_parameters['next_speed']
    flight_waypoints.version = flight.version
    yield flight_waypoints.put_async()
    response = {"Waypoint": [flight_waypoints.next_waypoint.lat, flight_waypoints.next_waypoint.lon], 
        "Dest Waypoint": [flight_waypoints.dest_waypoint.lat, flight_waypoints.dest_waypoint.lon], 
        "Speed": flight_waypoints.next_speed, 
        "Altitude": flight_waypoints.next_altitude}
    raise ndb.Return(response)


@app.route('/specific_waypoint_update', methods=['POST'])
def specific_waypoint_update():
    JSON = request.json
    flight_waypoints_key_urlsafe = JSON.get("flight_waypoints_key_urlsafe")
    flight_key_urlsafe = JSON.get("flight_key_urlsafe")
    flight_waypoints_key = ndb.Key(urlsafe=flight_waypoints_key_urlsafe)
    flight_key = ndb.Key(urlsafe=flight_key_urlsafe)
    response = execute_waypoint_update(flight_waypoints_key, flight_key)
    return jsonify(response)


@app.route('/waypoint_updates')
def waypoint_updates():
    done = execute_updates()
    if done:
        return "DONE!"


@app.route('/')
def hello_world():
    return 'Hello, World! This is a test!'

