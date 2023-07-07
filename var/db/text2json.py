import json
import sys
import pprint

content = None
with open("places_nautica.txt") as f:
    content = f.readlines()

result = {}

for line in content:
    line = line.replace("\n", "").replace("\r", "")
    # d03 13.1947 41.2797 13.2030 41.2892 LAZ_24 PORTO BADINO
    parts = line.split(" ")
    id = parts[5]
    minLon = float(parts[1])
    minLat = float(parts[2])
    maxLon = float(parts[3])
    maxLat = float(parts[4])
    name = ""
    for i in range(6, len(parts)):
        name = name + parts[i].capitalize() + " "

    # print id, name
    name = name.strip()
    long_name = name
    if "-" in name:
        parts = name.split("-")
        name = parts[0].strip()

    place = {
        "id": id,
        "long_name": {
            "it": long_name,
            "en": long_name
        },
        "maxLat": maxLat,
        "maxLon": maxLon,
        "minLat": minLat,
        "minLon": minLon,
        "name": {
            "it": name,
            "en": name
        }
    }

    result[id] = place

print(json.dumps(result))
