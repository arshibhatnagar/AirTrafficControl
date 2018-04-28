import requests
import sys
from concurrent.futures import ThreadPoolExecutor

URL = "http://localhost:8080/flight"

def first_post_url(url):
    return requests.post(url, json={'flight_num': "AA1234", "latitude": 43.578, "longitude": -64.341, "altitude": 123, 
        "speed": 123, "temperature": 32.4}).content

def start_concurrent_requests(num_requests, max_workers, flight_key_urlsafe, flight_waypoints_key_urlsafe):
    def post_url(url):
    return requests.post(url, json={'flight_num': "AA1234", "latitude": 43.578, "longitude": -64.341, "altitude": 123, 
        "speed": 123, "temperature": 32.4, 
        'flight_waypoints_key_urlsafe': flight_waypoints_key_urlsafe, 
        'flight_key_urlsafe': flight_key_urlsafe}).content

    url_list = [URL] * num_requests
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        print list(pool.map(post_url, url_list))


if __name__ == '__main__':
    num_requests = sys.argv[1]
    max_workers = sys.argv[2]
    initial_data = first_post_url(URL)
    flight_key_urlsafe = initial_data['flight_key_urlsafe']
    flight_waypoints_key_urlsafe = initial_data['flight_waypoints_key_urlsafe']
    start_concurrent_requests(num_requests, max_workers, flight_key_urlsafe, flight_waypoints_key_urlsafe)

