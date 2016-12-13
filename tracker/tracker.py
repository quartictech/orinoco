import requests
import math
import csv
import json
import geojson
import utils
import logging
import asyncio

from aiohttp import web

from orinoco import create_app

logging.basicConfig(level=logging.INFO, format='%(levelname)s [%(asctime)s] %(name)s: %(message)s')

queue = asyncio.Queue()

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

    logging.info("Processed {0} features".format(len(features)))
    queue.put_nowait({
        'timestamp' : 0,
        'featureCollection' : feature_collection
    })

    return web.Response(text=json.dumps(ret))

async def main_loop():
    while True:
        item = await queue.get()
        yield item

if __name__ == "__main__":
    app = create_app("tracker", main_loop)
    app.app.router.add_post('/upload', upload_handler)
    app.run()
