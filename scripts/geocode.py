import mapbox
from mapbox import Geocoder
geocoder = Geocoder()

def geocode(s):
    response = geocoder.forward("{0}, UK".format(s))
    return response.json()
#
# import requests
# from pprint import pprint
# key = "6D671032-591EDD2D-E1B046E4-9BA143DE-4360BA62-AD2AF05C-76BFBD11-9B23EBCD"
#
# r = requests.get("http://api.wikimapia.org/?function=place.search",
#     params = {
#         "key": key,
#         "q": "DYNEVOR LNG",
#         "lat": 51,
#         "lon": 0,
#         "distance": 1000000.0,
#         "format": "json"
#     })

import json
d = json.load(open("places.json"))
for name, place in d.items():
    geocoded = geocode(d[name]["address"] if "address" in d[name] else d[name]["name"])
    feature = geocoded["features"][0]
    d[name]["geocode"] = {
        "place_name": feature["place_name"],
        "geometry": feature["geometry"]
        }
json.dump(d, open("places.json.geocoded", "w"), indent=1)
