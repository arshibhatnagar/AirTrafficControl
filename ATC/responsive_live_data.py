from threading import Thread, Lock, Condition
import time
import sys
import requests
import os
import numpy as np
import json


URL = "http://localhost:8080/flight"
DATA_FILE = "../DataGenerators/Data/dynamic_data.json"
BACKEND_URL = "http://localhost:8081/waypoint_updates"

class Sensor(Thread):
    
    def __init__(self, id, data, delay):
        Thread.__init__(self)
        self.id = id
        self.flight_num = data['flight_num']
        self.origin = data['origin']
        self.destination = data['destination']
        self.latitudes = data['latitudes']
        self.longitudes = data['longitudes']
        self.temperatures = data['temperatures']
        self.speeds = data['speeds']
        self.altitudes = data['altitudes']
        self.delay = delay
        self.last = {"Waypoint" : [self.latitudes[0], self.longitudes[0]], "Speed": 400, "Altitude": 30400}
        self.next = self.last
        self.last_lat = None
        self.last_lon = None
        

    def run(self):
        time.sleep(self.delay)
        data = {}
        data['flight_num'] = self.flight_num
        data['latitude'] = self.latitudes[0]
        data['longitude'] = self.longitudes[0]
        data['temperature'] = self.temperatures[0]
        data['speed'] = self.speeds[0]
        data['altitude'] = self.altitudes[0]
        self.last_lat = data['latitude']
        self.last_lon = data['longitude']

        initial_data =  self.post_url(URL, data)
        flight_key_urlsafe = initial_data['flight_key_urlsafe']
        flight_waypoints_key_urlsafe = initial_data['flight_waypoints_key_urlsafe']
        data['flight_key_urlsafe'] = flight_key_urlsafe
        data['flight_waypoints_key_urlsafe'] = flight_waypoints_key_urlsafe

        time.sleep(12)
        for i in range(1, len(self.latitudes)):
            new_lat_interval, new_lon_interval = self.process_wp()
            self.last_lat = new_lat_interval
            self.last_lon = new_lon_interval
            data['latitude'], data['longitude'] = self.last_lat, self.last_lon
            data['temperature'] = self.temperatures[i%len(self.temperatures)]
            data['speed'] = self.next['Speed'] + np.random.randint(-20, 30)
            data['altitude'] = self.next['Altitude'] + np.random.randint(-200, 240)
            self.post_url(URL, data)
            time.sleep(12)

        os.exit(0)
    

    def process_wp(self):
        latitude = self.last_lat + (self.next["Waypoint"][0] - self.last["Waypoint"][0])/20.0
        longitude = self.last_lon + (self.next["Waypoint"][1] - self.last["Waypoint"][1])/20.0

        return latitude, longitude

    def post_url(self, url, data):
        msg = json.loads(requests.post(url, json=data).content)
        next_waypoint = msg["Waypoint"]
        if (next_waypoint != self.next["Waypoint"]):
            self.last = self.next
            self.next = msg
        return msg

if __name__ == "__main__":
    num_threads = int(sys.argv[1])
    file = open(DATA_FILE)
    data_list = json.load(file)
    threadpool = [Sensor(i, data_list[i], np.random.randint(0, 10)) for i in range(num_threads)]
    requests.get(BACKEND_URL)
    for thread in threadpool:
        thread.start()

       

