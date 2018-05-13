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
        self.delay = delay

        data1 = data[1]
        data2 = data[2]
        data = data[0]

        self.flight_num = data['flight_num']
        self.origin = data['origin']
        self.destination = data['destination']
        self.latitudes = data['latitudes']
        self.longitudes = data['longitudes']
        self.temperatures = data['temperatures']
        self.altitudes = data['altitudes']
        self.last = {"Waypoint" : [self.latitudes[0], self.longitudes[0]], "Speed": 400, "Altitude": 30400}
        self.next = self.last
        self.last_lat = None
        self.last_lon = None


        self.flight_num1 = data1['flight_num']
        self.origin1 = data1['origin']
        self.destination1 = data1['destination']
        self.latitudes1 = data1['latitudes']
        self.longitudes1 = data1['longitudes']
        self.temperatures1 = data1['temperatures']
        self.altitudes1 = data1['altitudes']
        self.last1 = {"Waypoint" : [self.latitudes1[0], self.longitudes1[0]], "Speed": 400, "Altitude": 30400}
        self.next1 = self.last1
        self.last_lat1 = None
        self.last_lon1 = None

        
        self.flight_num2 = data2['flight_num']
        self.origin2 = data2['origin']
        self.destination2 = data2['destination']
        self.latitudes2 = data2['latitudes']
        self.longitudes2 = data2['longitudes']
        self.temperatures2 = data2['temperatures']
        self.altitudes2 = data2['altitudes']
        self.last2 = {"Waypoint" : [self.latitudes2[0], self.longitudes2[0]], "Speed": 400, "Altitude": 30400}
        self.next2 = self.last2
        self.last_lat2 = None
        self.last_lon2 = None

        

    def run(self):
        time.sleep(self.delay)
        
        data = {}
        data1 = {}
        data2 = {}
        
        data['flight_num'] = self.flight_num
        data['latitude'] = self.latitudes[0]
        data['longitude'] = self.longitudes[0]
        data['temperature'] = self.temperatures[0]
        data['speed'] = 450
        data['altitude'] = self.altitudes[0]
        self.last_lat = data['latitude']
        self.last_lon = data['longitude']
        initial_data =  self.post_url(URL, data, 0)
        flight_key_urlsafe = initial_data['flight_key_urlsafe']
        flight_waypoints_key_urlsafe = initial_data['flight_waypoints_key_urlsafe']
        data['flight_key_urlsafe'] = flight_key_urlsafe
        data['flight_waypoints_key_urlsafe'] = flight_waypoints_key_urlsafe

        data1['flight_num'] = self.flight_num1
        data1['latitude'] = self.latitudes1[0]
        data1['longitude'] = self.longitudes1[0]
        data1['temperature'] = self.temperatures1[0]
        data1['speed'] = 450
        data1['altitude'] = self.altitudes1[0]
        self.last_lat1 = data1['latitude']
        self.last_lon1 = data1['longitude']
        initial_data1 =  self.post_url(URL, data, 1)
        flight_key_urlsafe1 = initial_data1['flight_key_urlsafe']
        flight_waypoints_key_urlsafe1 = initial_data1['flight_waypoints_key_urlsafe']
        data1['flight_key_urlsafe'] = flight_key_urlsafe1
        data1['flight_waypoints_key_urlsafe'] = flight_waypoints_key_urlsafe1

        data2['flight_num'] = self.flight_num2
        data2['latitude'] = self.latitudes2[0]
        data2['longitude'] = self.longitudes2[0]
        data2['temperature'] = self.temperatures2[0]
        data2['speed'] = 450
        data2['altitude'] = self.altitudes[0]
        self.last_lat2 = data2['latitude']
        self.last_lon2 = data2['longitude']
        initial_data2 =  self.post_url(URL, data, 2)
        flight_key_urlsafe2 = initial_data2['flight_key_urlsafe']
        flight_waypoints_key_urlsafe2 = initial_data2['flight_waypoints_key_urlsafe']
        data2['flight_key_urlsafe'] = flight_key_urlsafe2
        data2['flight_waypoints_key_urlsafe'] = flight_waypoints_key_urlsafe2

        time.sleep(12)

        for i in range(1, max(len(self.latitudes), max(len(self.latitudes1), len(self.latitudes2)))):
            new_lat_interval, new_lon_interval = self.process_wp(0)
            self.last_lat = new_lat_interval
            self.last_lon = new_lon_interval
            data['latitude'], data['longitude'] = self.last_lat, self.last_lon
            data['temperature'] = self.temperatures[i%len(self.temperatures)]
            data['speed'] = self.next['Speed'] + np.random.randint(-20, 30)
            data['altitude'] = self.next['Altitude'] + np.random.randint(-100, 100)
            self.post_url(URL, data, 0)
            
            new_lat_interval, new_lon_interval = self.process_wp(1)
            self.last_lat1 = new_lat_interval
            self.last_lon1 = new_lon_interval
            data1['latitude'], data1['longitude'] = self.last_lat1, self.last_lon1
            data1['temperature'] = self.temperatures2[i%len(self.temperatures1)]
            data1['speed'] = self.next1['Speed'] + np.random.randint(-20, 30)
            data1['altitude'] = self.next1['Altitude'] + np.random.randint(-200, 240)
            self.post_url(URL, data, 1)

            new_lat_interval, new_lon_interval = self.process_wp(2)
            self.last_lat2 = new_lat_interval
            self.last_lon2 = new_lon_interval
            data2['latitude'], data2['longitude'] = self.last_lat2, self.last_lon2
            data2['temperature'] = self.temperatures2[i%len(self.temperatures2)]
            data2['speed'] = self.next2['Speed'] + np.random.randint(-20, 30)
            data2['altitude'] = self.next2['Altitude'] + np.random.randint(-200, 240)
            self.post_url(URL, data, 2)


            time.sleep(12)

        os.exit(0)
    

    def process_wp(self, i):
        if i == 0:
            latitude = self.last_lat + (self.next["Waypoint"][0] - self.last["Waypoint"][0])/20.0
            longitude = self.last_lon + (self.next["Waypoint"][1] - self.last["Waypoint"][1])/20.0
        elif i == 1:
            latitude = self.last_lat1 + (self.next1["Waypoint"][0] - self.last1["Waypoint"][0])/20.0
            longitude = self.last_lon1 + (self.next1["Waypoint"][1] - self.last1["Waypoint"][1])/20.0
        elif i == 2:
            latitude = self.last_lat2 + (self.next2["Waypoint"][0] - self.last2["Waypoint"][0])/20.0
            longitude = self.last_lon2 + (self.next2["Waypoint"][1] - self.last2["Waypoint"][1])/20.0
        return latitude, longitude

    def post_url(self, url, data, i):
        msg = json.loads(requests.post(url, json=data).content)
        next_waypoint = msg["Waypoint"]
        if i == 0:
            if (next_waypoint != self.next["Waypoint"]):
                self.last = self.next
                self.next = msg
        elif i == 1:
            if (next_waypoint != self.next1["Waypoint"]):
                self.last1 = self.next1
                self.next1 = msg
        elif i == 2:
            if (next_waypoint != self.next2["Waypoint"]):
                self.last2 = self.next2
                self.next2 = msg
        return msg

if __name__ == "__main__":
    num_threads = int(sys.argv[1])
    file = open(DATA_FILE)
    data_list = json.load(file)
    threadpool = [Sensor(i, data_list[i:i+3], np.random.randint(0, 10)) for i in range(0, num_threads, 3)]
    requests.get(BACKEND_URL)
    for thread in threadpool:
        thread.start()

       

