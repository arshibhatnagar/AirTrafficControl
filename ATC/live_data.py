from threading import Thread, Lock, Condition
import time
import sys
import requests
import os
import numpy as np
import json


URL = "http://localhost:8080/flight"
DATA_FILE = "../DataGenerators/Data/dynamic_data.json"

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
        

    def run(self):
        time.sleep(self.delay)
        data = {}
        data['flight_num'] = self.flight_num
        data['latitude'] = self.latitudes[0]
        data['longitude'] = self.longitudes[0]
        data['temperature'] = self.temperatures[0]
        data['speed'] = self.speeds[0]
        data['altitude'] = self.altitudes[0]
        initial_data =  json.loads(self.post_url(URL, data))
        flight_key_urlsafe = initial_data['flight_key_urlsafe']
        flight_waypoints_key_urlsafe = initial_data['flight_waypoints_key_urlsafe']
        data['flight_key_urlsafe'] = flight_key_urlsafe
        data['flight_waypoints_key_urlsafe'] = flight_waypoints_key_urlsafe
        
        time.sleep(12)
        for i in range(1, len(self.latitudes)):
            data['latitude'] = self.latitudes[i]
            data['longitude'] = self.longitudes[i]
            data['temperature'] = self.temperatures[i]
            data['speed'] = self.speeds[i]
            data['altitude'] = self.altitudes[0]
            print self.post_url(URL, data)
            time.sleep(12)

        os.exit(0)
        

    def post_url(self, url, data):
       return requests.post(url, json=data).content

    
if __name__ == "__main__":
    num_threads = int(sys.argv[1])
    file = open(DATA_FILE)
    data_list = json.load(file)
    threadpool = [Sensor(i, data_list[i], np.random.randint(0, 5)) for i in range(num_threads)]
    for thread in threadpool:
        thread.start()

       

