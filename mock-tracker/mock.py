import requests
import math
import csv
import json
import geojson
import logging
import asyncio

from aiohttp import web

from orinoco import create_app

logging.basicConfig(level=logging.INFO, format='%(levelname)s [%(asctime)s] %(name)s: %(message)s')

schedule = []

async def upload_handler(request):
    data = await request.json()
    try:
        for f in data["features"]:
            timestamp = int(f["properties"]["timestamp"])
            del f["properties"]["timestamp"]
            schedule.append( (timestamp / 1000.0, f) )
    except Exception as e:
        logging.exception("Error processing request")
        return web.HTTPBadRequest()

    assert(schedule)
    schedule.sort(key=lambda x: x[0])

    logging.info("Processed {0} features".format(len(data['features'])))

    return web.Response()

async def main_loop():
    while True:
        timestamp = 0
        for ts, feature in schedule:
            await asyncio.sleep(ts - timestamp)
            yield({'timestamp' : timestamp, 'featureCollection':{'type' : 'FeatureCollection', 'features':[feature]}})
            timestamp = ts
        await asyncio.sleep(1)

if __name__ == "__main__":
    app = create_app("mock-tracker", main_loop)
    app.app.router.add_post('/upload', upload_handler)
    app.run()
