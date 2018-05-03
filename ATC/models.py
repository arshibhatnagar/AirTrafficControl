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
    flight_num = ndb.StringProperty()
    next_waypoint = ndb.GeoPtProperty()
    next_speed = ndb.FloatProperty()
    next_altitude = ndb.FloatProperty()
    flight_plan_urlsafe = ndb.StringProperty()
    flight_urlsafe = ndb.StringProperty()
    current_route_index = ndb.IntegerProperty()
    last_updated = ndb.DateTimeProperty(auto_now=True)

class Routes(ndb.Model):
    origin = ndb.StringProperty()
    destination = ndb.StringProperty()
    num_routes = ndb.IntegerProperty()
    routes = ndb.JsonProperty()
    # routes = ndb.StructuredProperty(Route, repeated=True)
    