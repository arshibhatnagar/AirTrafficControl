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
    flight_num = ndb.StringProperty()

# Stores the next waypoint for the flight to go to
class FlightWaypoints(ndb.Model):
    key = ndb.KeyProperty()
    flight_num = ndb.StringProperty()
    next_waypoint = ndb.GeoPtProperty()
    next_speed = ndb.IntegerProperty()
    next_altitude = ndb.IntegerProperty()
    