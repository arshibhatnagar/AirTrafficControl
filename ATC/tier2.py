# IN THE YAML FILE, SET INSTANCE CLASS TO INSTANCES WITH BIGGER MEMORY AND A FIXED NUMBER OF RUNNING INSTANCES
from flask import Flask, render_template, request, jsonify
from models import Flight, FlightPlan, FlightWaypoints
from google.appengine.ext import ndb
from google.appengine.api import memcache, taskqueue

app = Flask(__name__)
app.debug=True

client = memcache.Client()


flights_to_waypoints = {}
flights_to_altitudes = {}

@ndb.toplevel
@ndb.synctasklet
def execute_updates():
    waypoints_qry = FlightWaypoints.query().order(FlightWaypoints.version)
    results = yield waypoints_qry.fetch_async()
    flight_plan_keys = [ndb.Key(urlsafe=flight.flight_plan_urlsafe) for flight in results]
    flight_keys = [ndb.Key(urlsafe=flight.flight_urlsafe) for flight in results]
    flight_plans, flights = yield ndb.get_multi_async(flight_plan_keys), ndb.get_multi_async(flight_keys)
    new_flight_parameters = [flight.location for flight in flights]

    to_cache = {}

    for i in range(len(results)):
        flight_waypoints = results[i]
        flight = flights[i]
        flight_plan = flight_plans[i]

        new_parameters = {'next_waypoint': flight_waypoints.next_waypoint, 'next_speed': 975.0}
        if ((flight.location.lat- flight_waypoints.next_waypoint.lat)**2 + (flight.location.lon - flight_waypoints.next_waypoint.lon)**2)**0.5 < 0.08:
            if (flight_waypoints.current_route_index < len(flight_plan.current_route.waypoints) - 1):
                new_parameters['next_waypoint'] = flight_plan.current_route.waypoints[flight_waypoints.current_route_index + 1]
                flight_waypoints.current_route_index += 1

        

        next_wp = new_parameters['next_waypoint']
        flight_num = flight.flight_num

        
        # if flight_num in flights_to_altitudes:
        #     new_parameters['next_altitude'] = flights_to_altitudes[flight_num]
        #     print("HI")
        # else:

        new_parameters['next_altitude'] = flight.altitude
        if(abs(flight.altitude - 20000) < 200):
            new_parameters['next_altitude'] = 20000
            #print flights_to_altitudes
            #print("VAMOS BARCA")

        max_alt = 0
        flightlist = flights_to_waypoints.keys()
        for flight_id in flightlist:
            flight_wp = flights_to_waypoints[flight_id]
            if flight_id != flight_num:
                if ((next_wp.lat - flight_wp.lat)**2 + (next_wp.lon - flight_wp.lon)**2)**0.5 < 0.50:
                    if abs(new_parameters['next_altitude'] - flights_to_altitudes[flight_id]) < 370:
                        
                        print("Potential collision between " + str(flight_num) + " and " + str(flight_id) + " detected. Altitude adjustment initialized.")
                        print("Altitudes are: " + str(new_parameters['next_altitude']) + ", " +  str(flights_to_altitudes[flight_id]))
                        max_alt = max(max_alt, flights_to_altitudes[flight_id])
                        print ('max_alt is: ' + str(max_alt))
                        print("sdlfjasnkfjasnfkjasdfnlasdjfnaskdlfjnaslfjnasdlfasnldkfnsdljfnadslfjnasdlfjaslkfjnaskdflnasdlfnjsklfnasdfkljsdfnlkasdjfnkladsjn")
                        


                    
        if max_alt > 0:
            new_parameters["next_altitude"] = max_alt + 700
        else:
            a = 1
            #new_parameters['next_altitude'] = 20000.0
        # if new_parameters['next_altitude'] > 30000.0:
        #     a = 1
        #     print "High altitude " + str(new_parameters['next_altitude'])
        flights_to_altitudes[flight_num] = new_parameters["next_altitude"]
        flights_to_waypoints[flight_num] = next_wp
        #print('altitude for flight ' + str(flight_num) + ' is: ' + str(new_parameters['next_altitude']))

        flight_waypoints.next_waypoint = new_parameters['next_waypoint']
        flight_waypoints.next_altitude = new_parameters['next_altitude']
        flight_waypoints.next_speed = new_parameters['next_speed']
        flight_waypoints.version = flight.version

        #print(flights_to_altitudes)

        client.set(flight_waypoints.flight_urlsafe, flight_waypoints)

    yield ndb.put_multi_async(results)
        
    task = taskqueue.add(
            queue_name='backend',
            url='/waypoint_updates',
            method='GET')
    #print("HEEHEHEHEHEHEHEHEHEHE")
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

