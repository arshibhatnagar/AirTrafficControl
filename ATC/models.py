from google.appengine.ext import ndb

# Stores the current position of the flight
class Flight(ndb.Model):
    key = ndb.KeyProperty()
    flight_num = ndb.StringProperty()
    altitude = ndb.IntegerProperty()
    speed = ndb.IntegerProperty()
    location = ndb.GeoPtProperty()
    temperature = ndb.FloatProperty()

# Stores flight plans. This data does not change much.
class FlightPlan(ndb.Model):
    key = ndb.KeyProperty()
    #flight number should be a mixture of carrier code and number - will be used as key
    #to get all other attributes of the flight
    flight_num = ndb.StringProperty()
    origin = ndb.StringProperty()
    dest = ndb.StringProperty()
    #can combine date and time to make date time property for dep and arr
    dep_time = ndb.DateTimeProperty()
    arr_time = ndb.DateTimeProperty()
    cancelled = ndb.BooleanProperty()
    carrier = ndb.StringProperty()
    current_route = ndb.StructuredProperty(Route)


# Stores the next waypoint for the flight to go to
class FlightWaypoints(ndb.Model):
    key = ndb.KeyProperty()
    flight_num = ndb.StringProperty()
    next_waypoint = ndb.GeoPtProperty()
    next_speed = ndb.IntegerProperty()
    next_altitude = ndb.IntegerProperty()

class Route(ndb.Model):
    waypoints = ndb.GeoPtProperty(repeated=True)

class Routes(ndb.Model):
    origin = ndb.StringProperty()
    destination = ndb.StringProperty()
    num_routes = ndb.IntegerProperty()
    routes = ndb.StructuredProperty(Route, repeated=True)
    