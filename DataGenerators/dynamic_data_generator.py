import json
import sys
import numpy as np

latitude, longitude, altitude, speed, temperature



if __name__ == "__main__":
	file = open("Data/routes.txt")
	route_list = [json.loads(line) for line in file]
	indices = np.random.randint(175, size = 500)
	dynamic_data = []
	for i in indices:
		routes = route_list[i]
		origin = routes["origin"]
		destination = routes["destination"]
		chosen_route = np.random.randint(3)
		route = routes["routes"][chosen_route]
		distance = route['distance']
		waypoints = route['waypoints']
		latitudes = []
		longitudes = []
		altitudes = []
		speed = []
		temperature = []
		num_iter = int((distance/len(waypoints))/2)
		ground_temp = np.random.randint(2000, 10000)
		ground_altitude = np.random.randint(-1000, 2400)
		for i in range(len(waypoints)-1):
			lat1,lon1 = waypoints[i]
			lat2,lon2 = waypoints[i+1]
			lat_spread = (lat2 - lat1) / num_iter
			lon_spread = (lon2 - lon1) / lon_iter
			current_lat, current_lon = waypoints[i]
			for i in range(num_iter-1):
				latitudes.append(current_lat)
				longitudes.append(current_lon)
				altitude = min(np.random.randint(33000, 36000), min(waypoints))
				temp = min((ground_temp*100 - altitude)/100, -60 + 5*np.random.random())
				temperature.append(np.random.randint())
				current_lat += lat_spread + np.random.randint(-4, 4)*0.00003
				current_lon += lon_spread + np.random.randint(-4, 4)*0.00003

			latitudes.append(lat2)
			longitudes.append(lon2)
			temperatures.append(ground_temp)
			altitudes.append(ground_altitude)


		


