from . import backends
from kafka import KafkaProducer
from aiohttp import web
import asyncio

import logging
import sys
import json
import argparse

logging.basicConfig(level=logging.INFO, format='%(levelname)s [%(asctime)s] %(name)s: %(message)s')

class App(object):
    def __init__(self, name, backend, generator):
        self.count = 0
        self.name = name
        self.backend = backend
        self.generator = generator
        args = self.parse_args()
        self.port = args.port

    def parse_args(self):
        parser = argparse.ArgumentParser(
            description=self.name,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        parser.add_argument("-p", "--port", type=int, help="Port to serve on", default=8080)
        return parser.parse_args()

    async def run_async(self):
        #producer = KafkaProducer(bootstrap_servers="172.19.0.3:9092", acks=0)
        async for message in self.generator():
            if self.count % 10000 == 0:
                print(self.count)
            self.count += 1
            await self.backend.send(message)

    async def status(self, request):
        return web.Response(text=json.dumps({
            "message_count": self.count
        }))

    def run(self):
        app = web.Application()

        async def start_background_tasks(app):
            app['main_loop'] = app.loop.create_task(self.run_async())

        async def cleanup_background_tasks(app):
            app['main_loop'].cancel()

        app.on_startup.append(start_background_tasks)
        app.on_cleanup.append(cleanup_background_tasks)

        app.router.add_get('/' + self.name +'/healthcheck', self.status)
        resource = app.router.add_resource('/' + self.name, name=self.name)
        self.backend.register(resource)
        web.run_app(app, port=self.port)
