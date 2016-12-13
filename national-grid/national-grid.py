from utils import fetch_data
from collections import defaultdict
from pprint import pprint
import asyncio
import json
from datetime import datetime
import logging
import os.path

from orinoco import create_app

logging.basicConfig(level=logging.INFO, format='%(levelname)s [%(asctime)s] %(name)s: %(message)s')

data_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data", "places.json.geocoded")

places = json.load(open(data_path))
flows = defaultdict(dict)

def convert_time_series(d):
    for k, v in d.items():
        yield {
            "timestamp": int(k.strftime("%s")) * 1000,
            "value": v
        }

def send_time_series(key, data):
    if not key in places:
        logging.warn("key not found: " + key)
        return
    message = {
        "featureCollection": {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "id": key,
                    "geometry": places[key]["geocode"]["geometry"],
                    "properties": {
                        "name": key,
                        "Flow Rate": {
                            "type": "timeseries",
                            "series": list(convert_time_series(data))
                        }
                    }
                }
            ]
        },
        "timestamp": 0
    }
    return message

async def main_loop():
    await asyncio.sleep(5)
    while True:
        logging.info("processing...")
        result = fetch_data()
        for key, data in result["data"].items():
            if key == "TOTAL SUPPLY": continue
            time_series = flows[key]
            dirty = False
            for row in data:
                if not row['applicable_at']:
                    continue
                if not row['applicable_at'] in time_series:
                    time_series[row['applicable_at']] = row['flow_rate']
                    dirty = True
            if dirty:
                yield send_time_series(key, time_series)

        await asyncio.sleep(10)

if __name__ == "__main__":
    app = create_app("national-grid", main_loop)
    app.run()
