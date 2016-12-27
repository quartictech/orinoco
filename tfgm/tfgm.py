import requests
import asyncio
import logging
import json
from shapely.wkt import loads as wkt_loads
from shapely.geometry import LineString
from shapely.geometry.geo import mapping
import copy

from aiohttp import ClientSession

from orinoco import create_app

API_KEY = "59d6fca93351451f926abb841ee2f7bb"

def parse(data):
    features = []
    for item in data["value"]:
        if item["StartLocation"] and item["EndLocation"]:
            start = wkt_loads(item["StartLocation"]["LocationSpatial"]["Geography"]["WellKnownText"])
            end = wkt_loads(item["EndLocation"]["LocationSpatial"]["Geography"]["WellKnownText"])
            line = LineString([start.coords[0], end.coords[0]])

            properties = copy.copy(item)
            if item["ScootDetails"]:
                for k, v in item["ScootDetails"][0].items():
                    if k not in properties:
                        properties[k] = v
            del properties["StartLocation"]
            del properties["EndLocation"]
            del properties["ScootDetails"]
            features.append({
                "type": "Feature",
                "id": item["Id"],
                "properties": properties,
                "geometry": mapping(line.centroid)
            })
    logging.info("parsed %d features", len(features))
    return {
        "timestamp": 0,
        "featureCollection": {
            "type": "FeatureCollection",
            "features": features
        }
    }

async def loop():
    while True:
        logging.info("waking")
        url = "https://api.tfgm.com/odata/ScootLoops?$expand=StartLocation,EndLocation,ScootDetails"
        headers = { "Ocp-Apim-Subscription-Key": API_KEY}
        logging.info("requesting url: %s", url)
        async with ClientSession() as client:
            async with client.get(url, timeout=60, headers=headers) as r:
                r.raise_for_status()
                logging.info("waiting for response")
                data = await r.json()
                yield parse(data)
        logging.info("sleeping")
        await asyncio.sleep(5)

if __name__ == "__main__":
    app = create_app("tfgm", loop)
    app.run()
