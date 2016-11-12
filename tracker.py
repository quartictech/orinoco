import requests
import math
import csv
import json
import geojson
import utils
import logging

from aiohttp import web
import asyncio

logging.basicConfig(level=logging.INFO)

websockets = set()

async def post_events(e):
    for ws in websockets:
        ws.send_str(json.dumps(item))

async def upload_handler(request):
    data = await request.text()

    try:
        if request.headers.get('User-Agent') == 'androidSync/1.0':
            features = [utils.parse_xml(data)]
        else:
            features = utils.parse_csv(data)

        feature_collection = utils.prepare_feature_collection(features)
        ret = utils.prepare_return(features)
    except Exception as e:
        logging.exception("Error processing request")
        return web.HTTPBadRequest()

    await post_events({
        'timestamp' : 0,
        'featureCollection' : feature_collection
    })

    return web.Response(text=json.dumps(ret))

async def websocket_handler(request):
    logging.info("Registering websocket connection")
    global connected

    ws = web.WebSocketResponse()
    await ws.prepare(request)
    websockets.add(ws)

    async for msg in ws:
        pass

    logging.info("Unregistering websocket connection")
    websockets.remove(ws)

    return ws

async def status(request):
    return web.Response(text="Sweet")

if __name__ == "__main__":
    app = web.Application()
    app.router.add_get('/healthcheck', status)
    app.router.add_get('/tracker', websocket_handler)
    app.router.add_post('/upload', upload_handler)
    web.run_app(app)
