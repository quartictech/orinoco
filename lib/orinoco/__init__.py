from .app import App
from .backends import WebsocketBackend

def create_app(name, generator, metrics=None):
    return App(name, WebsocketBackend(), generator, metrics)
