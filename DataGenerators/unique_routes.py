import csv
import sys

def filter(filename):
	unique_routes = {}
	with open(filename, 'rb') as flightData:
		reader = csv.DictReader(flightData)
		for row in reader:
			origin = row['ORIGIN_AIRPORT_ID']
			destination = row['DEST_AIRPORT_ID']
			check = str(min(int(origin), int(destination))) + str(max(int(origin), int(destination)))
			if check not in unique_routes:
				unique_routes[check] = [row['ORIGIN'], row['DEST']]
	with open('unique_routes.csv', 'w') as csvfile:
		fieldnames = ['ORIGIN', 'DESTINATION']
		writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
		writer.writeheader()
		for value in unique_routes.values():
			writer.writerow({'ORIGIN': value[0], 'DESTINATION': value[1]})
	print len(unique_routes)

if __name__ == 'main':
	print sys.argv[1]
	filter(sys.argv[1])
