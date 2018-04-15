import json
import numpy as np

if __name__ == "__main__":
	num_points = int(input("What is the number of flights you want to generate data for?\n"))
	file = open("Data/routes.txt")
	route_list = [json.loads(line) for line in file]
	indices = np.random.randint(175, size = num_points)
	dynamic_data = []
	for i in indices:
		routes = route_list[i]
		#print(routes)
		origin = routes["origin"]
		destination = routes["destination"]
		#print(str(len(routes["routes"])))
		if len(routes["routes"]) < 1:
			print("oooh")
			continue
		route = routes["routes"][np.random.randint(len(routes["routes"]))]
		distance = route['distance']
		waypoints = route['waypoints']
		latitudes = []
		longitudes = []
		altitudes = []
		speeds = []
		temperatures = []
		num_iter = int((distance/len(waypoints))/2)
		ground_temp = np.random.randint(20, 88)
		for i in range(len(waypoints)-1):
			lat1,lon1 = waypoints[i]
			lat2,lon2 = waypoints[i+1]
			lat_spread = ((lat2 - lat1) / num_iter) + 0.0001
			lon_spread = ((lon2 - lon1) / num_iter) + 0.0001

			#print ("lat_spread " + str(lat_spread))
			#print ("long spread " + str(lon_spread))
				
			if lat_spread == 0.0 or lon_spread == 0.0:
				#print ("lat_spread " + str(lat_spread))
				#print ("long spread " + str(lon_spread))
				print("lat1 is " + str(lat1) + " and lat2 is " + str(lat2))
				print("lon1 is " + str(lon1) + " and lon2 is " + str(lon2))
				
			current_lat, current_lon = waypoints[i]
			for i in range(num_iter-1):
				latitudes.append(current_lat)
				longitudes.append(current_lon)
				altitude = min(np.random.randint(33000, 36000), 80000*min(abs(lat1 - current_lat), abs(current_lat - waypoints[-1][0])))/lat_spread
				temp = min((ground_temp*1000 - altitude)/100, -60 + 5*np.random.random())
				temperatures.append(temp)
				speeds.append(600 + 15*np.random.random())
				altitudes.append(altitude)
				current_lat += lat_spread + np.random.randint(-4, 4)*0.00003
				current_lon += lon_spread + np.random.randint(-4, 4)*0.00003

		latitudes.append(lat2)
		longitudes.append(lon2)
		temperatures.append(ground_temp)
		altitudes.append(np.random.randint(-400, 2400))
		speeds.append(0)

		#print(str(len(latitudes)) + " " + str(len(longitudes)) + " " + str(len(temperatures)) + " " + str(len(altitudes)) + " " + str(len(speeds)))

		datalog = {"origin": origin, "destination": destination, "latitudes": latitudes, "longitudes": longitudes, 
			"temperatures": temperatures, "altitudes": altitudes, "speeds": speeds}

		dynamic_data.append(datalog)
		
	#for data_point in dynamic_data:	
	with open("Data/dynamic_data.json", 'w') as file:
		json.dump(dynamic_data, file)
		

