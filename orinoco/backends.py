import logging
from aiohttp import web

class Backend(object):
    def send(self, message):
        pass

class WebsocketBackend(Backend):
    def __init__(self):
        self.websockets = []

    async def _websocket_handler(self, request):
        logging.info("Registering websocket connection")

        ws = web.WebSocketResponse()
        await ws.prepare(request)
        self.websockets.add(ws)

        async for msg in ws:
            pass

        logging.info("Unregistering websocket connection")
        websockets.remove(ws)
        return ws

    async def send(self, message):
        for ws in self.websockets:
            await ws.send_str(json.dumps(message))

    def register(self, resource):
        resource.add_route('GET', self._websocket_handler)
