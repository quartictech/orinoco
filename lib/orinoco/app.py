from . import backends
#from kafka import KafkaProducer
from aiohttp import web
import asyncio

import logging
import sys
import json
import argparse

from pyformance.registry import MetricsRegistry
from pyformance.reporters import ConsoleReporter

logging.basicConfig(level=logging.INFO, format='%(levelname)s [%(asctime)s] %(name)s: %(message)s')

class App(object):
    def __init__(self, name, backend, generator, metrics):
        self.name = name
        self.backend = backend
        self.generator = generator
        args = self.parse_args()
        self.port = args.port
        self.app = web.Application()
        self.fw_metrics = MetricsRegistry()
        reporter = ConsoleReporter(registry=self.fw_metrics)
        reporter.start()
        self.app_metrics = metrics
        if self.app_metrics:
            reporter = ConsoleReporter(registry=self.app_metrics)
            reporter.start()

    def parse_args(self):
        parser = argparse.ArgumentParser(
            description=self.name,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        parser.add_argument("-p", "--port", type=int, help="Port to serve on", default=8080)
        return parser.parse_args()

    def validate(self, message):
        assert "featureCollection" in message

    async def run_async(self):
        count = self.fw_metrics.meter("messages")
        features = self.fw_metrics.meter("features")
        while True:
            try:
                async for message in self.generator():
                    count.mark()
                    self.validate(message)

                    features.mark(len(message["featureCollection"]["features"]))

                    if count.get_count() % 10000 == 0:
                        print(count.get_count())
                    await self.backend.send(message)
            except Exception as e:
                logging.error("exception while running generator: %s", e)


    async def status(self, request):
        status = {
            "orinoco": self.fw_metrics.dump_metrics()
        }

        if self.app_metrics:
            status[self.name] = self.app_metrics.dump_metrics()

        return web.Response(text=json.dumps(status, indent=1))

    async def start_background_tasks(self, app):
        app['main_loop'] = app.loop.create_task(self.run_async())

    async def cleanup_background_tasks(self, app):
        app['main_loop'].cancel()


    def run(self):
        self.app.on_startup.append(self.start_background_tasks)
        self.app.on_cleanup.append(self.cleanup_background_tasks)

        self.app.router.add_get('/' + self.name +'/healthcheck', self.status)
        resource = self.app.router.add_resource('/' + self.name, name=self.name)
        self.backend.register(resource)
        web.run_app(self.app, port=self.port)
