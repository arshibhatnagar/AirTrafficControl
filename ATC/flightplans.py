import json
import csv
import requests

routes = {}
URL = "https://smart-atc.appspot.com/insert_flight_plan"

if __name__ == '__main__':
    with open('../DataGenerators/Data/routes.txt') as routes_handler:
        for row in routes_handler:
            route = json.loads(row)
            origin = route["origin"]
            destination = route["destination"]
            candidates = route["routes"]
            if len(candidates) == 0:
                continue
            shortestRoute = None
            for index in range(len(candidates)):
                new_route = candidates[index]
                if shortestRoute is None or new_route["distance"] < shortestRoute["distance"]:
                    shortestRoute = new_route
            routes[origin+destination] = shortestRoute["waypoints"]
            routes[destination+origin] = list(reversed(shortestRoute["waypoints"]))

    with open('../DataGenerators/Data/FlightPlans.csv') as flightData:
        reader = csv.DictReader(flightData)
        counter = 0
        for row in reader:
            # if counter >= 50:
            #     break
            flight_num = row['FL_NUM']
            origin = row['ORIGIN']
            dest = row['DEST']
            if (origin + dest not in routes):
                continue
            dep_date = '/'.join([row['YEAR'], row['MONTH'], row['DAY_OF_MONTH']])
            arr_date = dep_date # NEED TO CHECK FOR DAY CHANGE
            dep_time = ':'.join([row['DEP_TIME'][:-2], row['DEP_TIME'][-2:]])
            arr_time = ':'.join([row['ARR_TIME'][:-2], row['ARR_TIME'][-2:]])
            current_route = routes[origin+dest]
            carrier = row['UNIQUE_CARRIER']
            requests.post(URL, json={'flight_num': flight_num, 'origin': origin, 'dest': dest, 
                'dep_date': dep_date, 'arr_date': arr_date, 'dep_time': dep_time, 'arr_time': arr_time, 
                'current_route': current_route, 'carrier': carrier})
            counter += 1

    print "DONE!"

