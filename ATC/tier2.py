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
    # Can use the map function for tasklets. Look into that.
    results, cursor, more = yield waypoints_qry.fetch_page_async(page_size=20)
    # waypoints_qry_future = qry.fetch_page_async(page_size=500)
    # results, cursor, more = waypoints_qry_future.get_result()
    last_page = False
    if not more:
        last_page = True
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

        # TODO: COMPUTE new_flight_parameters TO TELL US WHAT THE NEXT WAYPOINT, SPEED AND ALTITUDE ARE
        new_flight_parameters = [flight.location for flight in flights]

        # flight_plan_future = ndb.get_multi_async(flights)
        # flight_plans = flight_plan_future.get_result()
        # Do async microservice calls here using an rpc created by urlfetch
        # Assuming a new flight parameters list is obtained from the microservice, for now just creating new_parameters

        for i in range(len(results)):
            flight_waypoints = results[i]
            flight = flights[i]
            flight_plan = flight_plans[i]

            # Let altitude and speed remain as is right now. Will have to change later
            new_parameters = {'next_waypoint': flight_waypoints.next_waypoint, 'next_altitude': 5000.0, 'next_speed': 975.0}

            # Update next waypoint if the currently assigned waypoint has been reached
            if ((flight.location.lat- flight_waypoints.next_waypoint.lat)**2 + (flight.location.lon - flight_waypoints.next_waypoint.lon)**2)**0.5 < 0.1:

                # for index in range(len(flight_plan.current_route)):
                #     if (flight.location.lat == flight_plan.current_route[index].lat and flight.location.lon == flight_plan.current_route[index].lon):
                #         if index == len(flight_plan.current_route) - 1:
                #             new_parameters['next_waypoint'] = None
                #         else:
                #             new_parameters['next_waypoint'] = flight_plan.current_route[index+1]

                new_parameters['next_waypoint'] = flight_plan.current_route[flight_waypoints.current_route_index + 1]
                flight_waypoints.current_route_index += 1

            flight_waypoints.next_waypoint = new_parameters['next_waypoint']
            flight_waypoints.next_altitude = new_parameters['next_altitude']
            flight_waypoints.next_speed = new_parameters['next_speed']

        yield ndb.put_multi_async(results)

        if more:
            results = next_results
            cursor = next_cursor
            more = next_more
        # put_future = ndb.put_multi_async(results)
        # put_future.get_result()
        # waypoints_qry_future = qry.fetch_page_async(page_size=500, cursor=cursor)
        # results, cursor, more = waypoints_qry_future.get_result()
    raise ndb.Return(True)

# Could get all the data and do all the updates and write to cache
# Could get paginated data, and do updates asynchronously for each page
# Cron job task
# Need to figure out caching policy for tier 1.
@app.route('/waypoint_updates')
def waypoint_updates():
    done = execute_updates()
    if done:
        return "DONE!"
