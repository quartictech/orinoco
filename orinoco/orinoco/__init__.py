from .app import App
from .backends import WebsocketBackend

def create_app(name, generator):
    return App(name, WebsocketBackend(), generator)
