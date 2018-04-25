from flask import Flask, render_template, request
from models import Flight, FlightPlan, FlightWaypoints
from google.appengine.ext import ndb

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World! This is a test!'

# Could get all the data and do all the updates and write to cache
# Could get paginated data, and do updates asynchronously for each page
# Cron job task
# Need to figure out caching policy for tier 1.
@app.route('/waypoint_updates')
def waypoint_updates():
    waypoints_qry = FlightWaypoints.query().order(-FlightWaypoints.datetime)
    # Can use the map function for tasklets. Look into that.
    results, cursor, more = qry.fetch_page(page_size=500)
    # waypoints_qry_future = qry.fetch_page_async(page_size=500)
    # results, cursor, more = waypoints_qry_future.get_result()
    last_page = False
    if not more:
        last_page = True
    while (more or last_page):
        if (last_page):
            last_page = False
        flight_plan_keys = [ndb.Key(FlightPlan, flight.flight_num) for flight in results]
        flight_plans = ndb.get_multi(flight_plan_keys)
        flights = [ndb.Key(Flight, flight.flight_num) for flight in results]

        # TODO: COMPUTE new_flight_parameters TO TELL US WHAT THE NEXT WAYPOINT, SPEED AND ALTITUDE ARE


        # flight_plan_future = ndb.get_multi_async(flights)
        # flight_plans = flight_plan_future.get_result()
        # Do async microservice calls here using an rpc created by urlfetch
        for i in range(len(results)):
            flight = results[i]
            new_parameters = new_flight_parameters[i] # Assuming a new flight parameters list is obtained from the microservice
            flight.next_waypoint = new_parameters['next_waypoint']
            flight.next_altitude = new_parameters['next_altitude']
            flight.next_speed = new_parameters['next_speed']

        ndb.put_multi([result.key for result in results])
        # put_future = ndb.put_multi_async(results)
        # put_future.get_result()
        # waypoints_qry_future = qry.fetch_page_async(page_size=500, cursor=cursor)
        # results, cursor, more = waypoints_qry_future.get_result()
        if more:
            results, cursor, more = qry.fetch_page(page_size=500)
        if (not more):
            last_page = True
