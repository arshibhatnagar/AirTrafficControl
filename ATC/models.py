from google.appengine.ext import ndb

# SET INDEXED TO FALSE FOR FASTER WRITES

# Stores the current position of the flight
class Flight(ndb.Model):
    # key = ndb.KeyProperty()
    flight_num = ndb.StringProperty(indexed=False)
    altitude = ndb.FloatProperty(indexed=False)
    speed = ndb.FloatProperty(indexed=False)
    location = ndb.GeoPtProperty(indexed=False)
    temperature = ndb.FloatProperty(indexed=False)
    version = ndb.IntegerProperty()

class Route(ndb.Model):
    waypoints = ndb.GeoPtProperty(repeated=True)

# Stores flight plans. This data does not change much.
class FlightPlan(ndb.Model):
    # key = ndb.KeyProperty()
    #flight number should be a mixture of carrier code and number - will be used as key
    #to get all other attributes of the flight
    flight_num = ndb.StringProperty()
    origin = ndb.StringProperty(indexed=False)
    dest = ndb.StringProperty(indexed=False)
    #can combine date and time to make date time property for dep and arr
    dep_time = ndb.DateTimeProperty(indexed=False)
    arr_time = ndb.DateTimeProperty(indexed=False)
    cancelled = ndb.BooleanProperty(indexed=False)
    carrier = ndb.StringProperty(indexed=False)
    current_route = ndb.StructuredProperty(Route)

# Stores the next waypoint for the flight to go to
class FlightWaypoints(ndb.Model):
    # key = ndb.KeyProperty()
    flight_num = ndb.StringProperty(indexed=False)
    next_waypoint = ndb.GeoPtProperty(indexed=False)
    dest_waypoint = ndb.GeoPtProperty(indexed=False)
    next_speed = ndb.FloatProperty(indexed=False)
    next_altitude = ndb.FloatProperty(indexed=False)
    flight_plan_urlsafe = ndb.StringProperty(indexed=False)
    flight_urlsafe = ndb.StringProperty(indexed=False)
    current_route_index = ndb.IntegerProperty(indexed=False)
    last_updated = ndb.DateTimeProperty(auto_now=True)
    version = ndb.IntegerProperty()

class Routes(ndb.Model):
    origin = ndb.StringProperty(indexed=False)
    destination = ndb.StringProperty(indexed=False)
    num_routes = ndb.IntegerProperty(indexed=False)
    routes = ndb.JsonProperty(indexed=False)
    # routes = ndb.StructuredProperty(Route, repeated=True)
    