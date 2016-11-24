from utils import fetch_data
from collections import defaultdict
from pprint import pprint
from aiohttp import web
import asyncio
import json
from datetime import datetime
import logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s [%(asctime)s] %(name)s: %(message)s')

places = json.load(open("data/places.json.geocoded"))
flows = defaultdict(dict)

async def status(request):
    return web.Response(text="Sweet")

websockets = set()

async def send_event(event):
    for ws in websockets:
        ws.send_str(json.dumps(event))

def convert_time_series(d):
    for k, v in d.items():
        yield {
            "timestamp": int(k.strftime("%s")) * 1000,
            "value": v
        }

async def send_time_series(key, data):
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
    await send_event(message)

async def main_loop(app):
    await asyncio.sleep(5)
    while True:
        logging.info("processing...")
        logging.info("open websockets: %d", len(websockets))
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
                await send_time_series(key, time_series)

        await asyncio.sleep(1)

async def websocket_handler(request):
    logging.info("Registering websocket connection")
    global websockets

    ws = web.WebSocketResponse()
    await ws.prepare(request)
    websockets.add(ws)

    # Send all data on startup
    logging.info("sending initial time series")
    for key, time_series in flows.items():
        await send_time_series(key, time_series)

    async for msg in ws:
        pass

    logging.info("Unregistering websocket connection")
    websockets.remove(ws)

    return ws

async def start_background_tasks(app):
    app['main_loop'] = app.loop.create_task(main_loop(app))

async def cleanup_background_tasks(app):
    app['main_loop'].cancel()

if __name__ == "__main__":
    app = web.Application()
    app.on_startup.append(start_background_tasks)
    app.on_cleanup.append(cleanup_background_tasks)
    app.router.add_get('/healthcheck', status)
    app.router.add_get('/ng', websocket_handler)
    web.run_app(app, port=9000)
