from flask import Flask, render_template, request
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
    waypoints_qry_future = qry.fetch_page_async(page_size=500)
    results, cursor, more = waypoints_qry_future.get_result()
    while (more): # Last page won't be served
        flights = [ndb.Key(FlightPlan, flight.flight_num) for flight in results]
        flight_plan_future = ndb.get_multi_async(flights)
        flight_plans = flight_plan_future.get_result()
        # Do async microservice calls here using an rpc created by urlfetch
        # Assuming a new flight waypoints list is obtained from the microservice
        for i in range(len(results)):
            flight = results[i]
            new_waypoint = new_flight_waypoints[i]
            flight.next_waypoint = new_waypoint
        put_future = ndb.put_multi_async(results)
        put_future.get_result()
        waypoints_qry_future = qry.fetch_page_async(page_size=500, cursor=cursor)
        results, cursor, more = waypoints_qry_future.get_result()
