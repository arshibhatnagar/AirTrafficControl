# IN THE YAML FILE, SET INSTANCE CLASS TO INSTANCES WITH BIGGER MEMORY AND A FIXED NUMBER OF RUNNING INSTANCES
from flask import Flask, render_template, request
from models import Flight, FlightPlan, FlightWaypoints
from google.appengine.ext import ndb

app = Flask(__name__)
app.debug=True

@app.route('/')
def hello_world():
    return 'Hello, World! This is a test!'

@ndb.toplevel
@ndb.synctasklet
def execute_updates():
    waypoints_qry = FlightWaypoints.query().order(FlightWaypoints.last_updated)
    results, cursor, more = yield waypoints_qry.fetch_page_async(page_size=20)
    last_page = False
    if not more:
        last_page = True
    next_waypoints = {}
    next_altitudes - {}
    while (more or last_page):
        if (last_page):
            last_page = False
        if more:
            next_results, next_cursor, next_more = yield waypoints_qry.fetch_page_async(page_size=20, start_cursor=cursor)
            if (not next_more):
                last_page = True

        flight_plan_keys = [ndb.Key(urlsafe=flight.flight_plan_urlsafe) for flight in results]
        flight_keys = [ndb.Key(urlsafe=flight.flight_urlsafe) for flight in results]
        flight_plans, flights = yield ndb.get_multi_async(flight_plan_keys), ndb.get_multi_async(flight_keys)

        new_flight_parameters = [flight.location for flight in flights]

        for i in range(len(results)):
            flight_waypoints = results[i]
            flight = flights[i]
            flight_plan = flight_plans[i]

            new_parameters = {'next_waypoint': flight_waypoints.next_waypoint, 'next_altitude': 5000.0, 'next_speed': 975.0}
            if ((flight.location.lat- flight_waypoints.next_waypoint.lat)**2 + (flight.location.lon - flight_waypoints.next_waypoint.lon)**2)**0.5 < 0.1:

                new_parameters['next_waypoint'] = flight_plan.current_route[flight_waypoints.current_route_index + 1]
                flight_waypoints.current_route_index += 1


            next_wp = new_parameters['next_waypoint']
            if next_wp in next_waypoints:
                new_parameters['altitude'] = next_waypoints[next_wp][-1] + 500
                next_waypoints[next_wp].append(new_parameters['altitude'])
            else:
                new_parameters['altitude'] = 29000
                next_waypoints[next_wp] = [29000]
            
            flight_waypoints.next_waypoint = new_parameters['next_waypoint']
            flight_waypoints.next_altitude = new_parameters['next_altitude']
            flight_waypoints.next_speed = new_parameters['next_speed']            
        yield ndb.put_multi_async(results)

        if more:
            results = next_results
            cursor = next_cursor
            more = next_more
        
    raise ndb.Return(True)


@app.route('/waypoint_updates')
def waypoint_updates():
    done = execute_updates()
    if done:
        return "DONE!"
