from threading import Thread, Lock, Condition
import time
import sys
import requests
import os
import numpy as np


URL = "https://smart-atc.appspot.com/flight"
DATA_FILE = "Data/dynamic_data.json"

class Sensor(Thread):
    
    def __init__(self, id, data, delay):
        self.id = id
        self.flight_num = data['flight_num']
        self.origin = data['origin']
        self.destination = data['destination']
        self.latitudes = data['latitudes']
        self.longitudes = data['longitudes']
        self.temperatures = data['temperature']
        self.speeds = data['speeds']
        self.delay = delay
        

    def run():
        self.sleep(delay)
        data = {}
        data['flight_num'] = "AI" + str(10000*np.random.random())
        data['latitude'] = latitudes[0]
        data['longitude'] = longitudes[0]
        data['temperature'] = temperatures[0]
        data['speed'] = speeds[0]
        initial_data =  self.post_url(URL, data)
        flight_key_urlsafe = initial_data['flight_key_urlsafe']
        flight_waypoints_key_urlsafe = initial_data['flight_waypoints_key_urlsafe']
        data['flight_key_urlsafe'] = flight_key_urlsafe
        data['flight_waypoints_key_urlsafe'] = flight_waypoints_key_urlsafe
        
        self.sleep(12)
        for i in range(1, len(latitudes)):
            data['latitude'] = latitudes[i]
            data['longitude'] = longitudes[i]
            data['temperature'] = temperatures[i]
            data['speed'] = speeds[i]
            self.post_url(URL, data)
            self.sleep(12)

        os.exit(0)
        

    def post_url(url, data):
       return requests.post(url,data).content

    
if __name__ == "__main__":
    num_threads = sys.argv[1]
    file = open(DATA_FILE)
    data_list = json.load(file)
    threadpool = [Sensor(i, data_list[i], np.random.randint(0, 750)) for i in range(num_threads)]
    for thread in threadpool:
        thread.start()

       

