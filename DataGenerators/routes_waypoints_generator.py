import requests
import json
import csv
import sys

API_KEY = 'Q1j7ryyP8qzzpAFzdzAwAvxMgGNw75QhLSSZjRb5'

def fetchData(filename):
	counter = 0
	with open(filename, 'rb') as routeData:
		reader = csv.DictReader(routeData)
		with open('routes.txt', 'w') as writer:
			for row in reader:
				origin = 'K' + row['ORIGIN']
				dest = 'K' + row['DESTINATION']
				contents1 = requests.get("https://api.flightplandatabase.com/search/plans?fromICAO=" + origin + "&toICAO=" + dest + "&includeRoute=true&limit=1&page=1", auth=(API_KEY,''))
				contents2 = requests.get("https://api.flightplandatabase.com/search/plans?fromICAO=" + origin + "&toICAO=" + dest + "&includeRoute=true&limit=1&page=2", auth=(API_KEY,''))
				contents3 = requests.get("https://api.flightplandatabase.com/search/plans?fromICAO=" + origin + "&toICAO=" + dest + "&includeRoute=true&limit=1&page=3", auth=(API_KEY,''))
				contents = [contents1, contents2, contents3]
				jsons = [content.json() for content in contents]
				routes = [json_object[0]['route'] for json_object in jsons if len(json_object) > 0]
				distances = [json_object[0]['distance'] for json_object in jsons if len(json_object) > 0]
				waypointsList = [[(node['lat'], node['lon']) for node in route['nodes']] for route in routes]
				d = {'origin': row['ORIGIN'], 'destination': row['DESTINATION'], 'routes': []}
				for index in range(len(routes)):
					d['routes'].append({'waypoints': waypointsList[index], 'distance': distances[index]})
				json.dump(d, writer)
				writer.write("\n")
				counter += 1
				print str(counter)

if __name__ == '__main__':
	fetchData(sys.argv[1])

