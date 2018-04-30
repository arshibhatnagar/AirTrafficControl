import json
import numpy as np
import sys
import csv

if __name__ == "__main__":
    num_points = int(sys.argv[1])
    file = open("Data/routes.txt")
    route_list = [json.loads(line) for line in file]
    indices = np.random.randint(175, size = num_points)
    flight_number = 105
    dynamic_data = []
    for i in indices:
        flight_num = "AI" + str(flight_number)
        routes = route_list[i]
        #print(routes)
        origin = routes["origin"]
        destination = routes["destination"]
        #print(str(len(routes["routes"])))
        if len(routes["routes"]) < 1:
            #print("oooh")
            continue
        shortestRoute = None
        candidates = routes["routes"]
        for index in range(len(candidates)):
            new_route = candidates[index]
            if shortestRoute is None or new_route["distance"] < shortestRoute["distance"]:
                shortestRoute = new_route
        route = shortestRoute
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
                altitude = np.random.randint(33000, 36000)
                if altitude < -20000 or altitude > 40000:
                    print(altitude)
                temp = min((ground_temp*1000 - altitude)/100, -60 + 5*np.random.random())
                if temp < -1000:
                    print("temp is " + str(temp))
                    print("altitude is" + str(altitude))
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

        datalog = {"flight_num": flight_num, "origin": origin, "destination": destination, "latitudes": latitudes, "longitudes": longitudes, 
            "temperatures": temperatures, "altitudes": altitudes, "speeds": speeds}
        dynamic_data.append(datalog)

        flight_number += 1
        
    #for data_point in dynamic_data:

    airline_codes = ['AI', 'UA', 'AA', 'EK', 'EA', 'EY', 'KL', 'DL', 'LH', 'BA']
    fieldnames=['YEAR', 'MONTH', 'DAY_OF_MONTH', 'UNIQUE_CARRIER', 'FL_NUM', 'ORIGIN', 'DEST', 'DEP_TIME', 'ARR_TIME', 'CANCELLED' ]
    
    with open("Data/flightplans.csv", 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        j = 105
        for log in dynamic_data:
            rand = np.random.randint(0, len(airline_codes))
            dep_time = str(500 + min(59, 10*j/800 + np.random.randint(0,5))).rjust(4, '0')
            arr_time = str(100*(np.random.randint(0,1400)/100) + min(59, 10*j/800 + np.random.randint(0,5))).rjust(4, '0')
            
            writer.writerow({'YEAR': 2018, 'MONTH': 6, 'DAY_OF_MONTH': 10, 'UNIQUE_CARRIER': "AI", 'FL_NUM': log['flight_num'], 
                'ORIGIN':log['origin'], 'DEST':log['destination'], 'DEP_TIME': dep_time, 'ARR_TIME': arr_time, 'CANCELLED': False})
            j += 1
    
    with open("Data/dynamic_data.json", 'w') as file:
        json.dump(dynamic_data, file)
            

