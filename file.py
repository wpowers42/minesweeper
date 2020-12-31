import json

location_file = 'location.json'

def read_location(location_file=location_file):
	with open(location_file, 'r') as file:
		data = json.load(file)
		return tuple(data.values())

def write_location(location, location_file=location_file):
	with open(location_file, 'w') as file:
		(left, top, width, height) = location
		data = {
			'left': int(location.left),
			'top': int(location.top),
			'width': int(location.width),
			'height': int(location.height)
		}
		print(data)
		json.dump(data, file)