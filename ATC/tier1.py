from flask import Flask, render_template, request, jsonify
from models import Flight, FlightWaypoints
from google.appengine.ext import ndb
from threading import Condition

app = Flask(__name__)
app.debug=True

flight_update_list = []
update_cv = Condition()
updating = False

# TRYING TO DO BATCHING

@app.route('/')
def hello_world():
    # print "Hello"
    new_flight = FlightWaypoints(
        flight_num="AA1234", next_waypoint=ndb.GeoPt(42.234, -56.345), 
        next_speed=123, next_altitude=345)
    # AA1234 = ndb.Key(FlightWaypoints, "AA1234")
    # print "flight waypoints key is: "
    # print AA1234
    # new_flight.key = AA1234
    flight_waypoint_key = new_flight.put()
    return 'Hello, World! This is a test!' + flight_waypoint_key.urlsafe()

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

def update_or_insert(flight, flight_key_urlsafe):
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


    # flight_key = ndb.Key(urlsafe=)
    # fetched = flight_key.get()
    # if fetched is not None:
    #     fetched.location = flight.location
    #     fetched.altitude = flight.altitude
    #     fetched.speed = flight.speed
    #     fetched.temperature = flight.temperature
    #     return fetched.put()
    # else:
    #     return flight.put()

def push_updates():
    global flight_update_list
    global updating
    # print "IN PUSH"
    # print "LEN OF FLIGHT_UPDATE_LIST IS: " + str(len(flight_update_list))
    update_cv.acquire()
    if (len(flight_update_list) >= 30):
        updating = True
        # print "PUSHING UPDATES"
        new_flights, urlsafes = map(list, zip(*flight_update_list))
        flight_keys = [ndb.Key(urlsafe=urlsafe) for urlsafe in urlsafes]
        flights = ndb.get_multi(flight_keys)
        for index in range(len(flights)):
            flight = flights[index]
            new_flight = new_flights[index]
            flight.location = new_flight.location
            flight.altitude = new_flight.altitude
            flight.speed = new_flight.speed
            flight.temperature = new_flight.temperature
        ndb.put_multi(flights)
        flight_update_list = []
        updating = False
        update_cv.notify_all()
    update_cv.release()


def retrieve_next_data(flight_waypoints_key_urlsafe):
    flight_waypoints_key = ndb.Key(urlsafe=flight_waypoints_key_urlsafe)
    fetched = flight_waypoints_key.get()
    return {"Waypoint": [fetched.next_waypoint.lat, fetched.next_waypoint.lon], "Speed": fetched.next_speed, "Altitude": fetched.next_altitude}

@app.route('/flight', methods=['POST'])
def incoming_flight_data():
    global flight_update_list
    global updating
    global update_cv
    # print "in flight"
    JSON = request.json
    flight_num = JSON.get('flight_num')
    latitude = JSON.get('latitude')
    longitude = JSON.get('longitude')
    altitude = JSON.get('altitude')
    speed = JSON.get('speed')
    temperature = JSON.get('temperature')

    flight = Flight(flight_num=flight_num, location=ndb.GeoPt(latitude, longitude), 
        altitude=altitude, speed=speed, temperature=temperature)

    flight_key_urlsafe = None
    flight_waypoints_key_urlsafe = JSON.get('flight_waypoints_key_urlsafe') # CHANGE THIS
    if 'flight_key_urlsafe' in JSON:
        flight_key_urlsafe = JSON.get('flight_key_urlsafe')
        flight_waypoints_key_urlsafe = JSON.get('flight_waypoints_key_urlsafe')
    
    data = retrieve_next_data(flight_waypoints_key_urlsafe)
    if flight_key_urlsafe is None:
        flight_key = update_or_insert(flight, flight_key_urlsafe)
        flight_key_urlsafe_to_send = flight_key.urlsafe()
        data['flight_key_urlsafe'] = flight_key_urlsafe_to_send

    else:
        update_cv.acquire()
        while (updating):
            update_cv.wait()
        # print "APPENDING"
        flight_update_list.append((flight, flight_key_urlsafe))
        update_cv.release()

    push_updates()

        
    # flight_key = ndb.Key(Flight, flight_num)
    # print "Flight key is: "
    
    # flight.key = flight_key

    # data = {'flight_num': "flight_num", "latitude": 43.578, "longitude": -64.341, "altitude": 123, "speed": 123, "temperature": 32.4}
        
    
    # update_or_insert_tasklet(flight_key, flight)

    # flight_waypoints_key = ndb.Key(FlightWaypoints, flight_num)
    # print flight_waypoints_key.pairs()
    

    return jsonify(data)

    # Look into using get_or_insert
    # Want to do this batched
    # Want to check cache
    # Want to communicate with tier 2 to get the data for the flight