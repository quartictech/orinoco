import requests
import json
import csv
import time
from collections import defaultdict, OrderedDict
import geojson
import datetime
import shapely.geometry as SG
from shapely.geometry import LineString
import logging

from aiohttp import web
import asyncio

logging.basicConfig(level=logging.INFO, format='%(levelname)s [%(asctime)s] %(name)s: %(message)s')

# APP_ID="4abd99df"
# APP_KEY="0f76ba70a21836b0991d192dceae511b"
APP_ID = "860e7675"
APP_KEY = "1d36a20279e6ac727ddfdcaeba2e97ea"

FIELDS = [
        "stationName",
        "destinationName",
        "expectedArrival",
        "naptanId",
        "vehicleId",
        "destinationNaptanId",
        "direction",
        "timestamp",
        "timeToStation",
        "currentLocation",
        "id",
        "bearing",
        "towards",
        "lineId",
        "lineName"
]

websockets = set()

async def send_event(event):
    for ws in websockets:
        ws.send_str(json.dumps(event))

def request(path, **kwargs):
    url = "https://api.tfl.gov.uk{path}?app_id={app_id}&app_key={app_key}".format(path=path, app_id=APP_ID, app_key=APP_KEY)
    r = requests.get(url, timeout=60)
    return r.json()

def lookup_station(station_id, station_locs={}):
    if station_id not in stations_locs.keys():
        r = request("/StopPoint/{}".format(station_id))
        station_locs[station_id] = (r['lat'], r['lon'])
    return station_locs[station_id]

def lookup_line_path(line_id, direction):
    r = request("/Line/{}/Route/Sequence/{}".format(line_id, direction))
    assert len(r['lineStrings']) == 1
    assert len(json.loads(r['lineStrings'][0])) == 1
    return LineString(json.loads(r['lineStrings'][0])[0])

def lookup_line(line_id):
    stops_direction = {}
    for direction in ['inbound', 'outbound']:
        r = request("/Line/{}/Route/Sequence/{}".format(line_id, direction))
        stop_points =  r['stopPointSequences'][0]
        stops = OrderedDict()
        for stop in stop_points['stopPoint']:
            stops[stop['id']] = (stop['name'], stop['lat'], stop['lon'])
        stops_direction[direction] = stops
    return stops_direction

def fetch_arrival_predictions(line):
    bus_arrivals = {}
    r = request("/line/{0}/arrivals".format(line))
    for arrival in r:
        bus_id = arrival['vehicleId']
        if bus_id in bus_arrivals.keys():
            bus_arrivals[bus_id].append(arrival)
        else:
            bus_arrivals[bus_id] = [arrival]
    return {bus_id: min(arrivals, key=lambda k: k['timeToStation']) for bus_id, arrivals in bus_arrivals.items()}

def previous_stop(bus_arrival, line_info):
    """Returns the previous stop to the current stop for the line."""
    next_stop = bus_arrival['naptanId']
    line_direction = line_info[bus_arrival['direction']]
    next_index = list(line_direction.keys()).index(next_stop)
    return list(line_direction.values())[next_index-1]

def current_stop(bus_arrival, line_info):
    current_stop = bus_arrival['naptanId']
    line_direction = line_info[bus_arrival['direction']]
    try:
        return line_direction[current_stop]
    except KeyError as e:
        logging.exception("Error")
        return None

def current_stops(bus_arrivals, line_info, current):
    for bus_id, bus_arrival in bus_arrivals.items():
            current[bus_id] = current_stop(bus_arrival, line_info)
    return current

def get_position(current, next_pos, proportion):
    segment = LineString(((current[2], current[1]), (next_pos[2], next_pos[1])))
    return segment.interpolate(distance=proportion, normalized=True)

def time_to_station(bus_arrivals, time_to_dest):
    """Returns total time estimated to next stop for each bus ID."""
    for bus_id, bus_arrival in bus_arrivals.items():
        new_prediction = bus_arrival['timeToStation']
        if (bus_id not in time_to_dest.keys()) or (time_to_dest[bus_id] <= new_prediction):
            time_to_dest[bus_id] = new_prediction
    return time_to_dest

def estimate_to_station(bus_arrivals, next_stop, line_info, eta, interpol_dt):
    for bus_id, bus_arrival in bus_arrivals.items():
        new_prediction = bus_arrival['timeToStation']
        if bus_id in eta.keys():
            if eta[bus_id] > new_prediction:
                eta[bus_id] = new_prediction
            elif (eta[bus_id] < new_prediction and
            next_stop[bus_id] != current_stop(bus_arrival, line_info)):
                eta[bus_id] = new_prediction
            elif eta[bus_id] > interpol_dt:
                eta[bus_id] = eta[bus_id] - interpol_dt
            else:
                eta[bus_id] = 0
        else:
            eta[bus_id] = new_prediction
    return eta

def prepare_geojson(line_id, bus_id, pos):
    bus_feature = geojson.Feature(id=bus_id, geometry=pos, properties={
        'vehicle id': bus_id,
        'route': line_id
    })
    return bus_feature

async def prepare_event(line_ids, line_info, bus_arrivals, time_to_dest, eta, path):
    collection = []

    for line_id in line_ids:
        for bus_id, bus_arrival in bus_arrivals[line_id].items():
            try:
                previous = previous_stop(bus_arrival, line_info[line_id])
                current = current_stop(bus_arrival, line_info[line_id])
                proportion = eta[line_id][bus_id] / time_to_dest[line_id][bus_id]

                pos = get_position(current, previous, proportion)
                pos = path[line_id].interpolate(path[line_id].project(pos, normalized=True),normalized=True)#attempt to get it on the line
                collection.append(prepare_geojson(line_id, bus_id, pos))
            except Exception as e:
                logging.exception("Error")

    logging.info("Processed {0} features".format(len(collection)))
    await send_event({
        'timestamp' : 0,
        'featureCollection' : geojson.FeatureCollection(collection)
    })

##############################################################################

class Api:
    def get_stop(self, stop_id):
        return self._request("/StopPoint/{}".format(stop_id))

    def get_line(line_id, direction):
        return self._request("/Line/{}/Route/Sequence/{}".format(line_id, direction))

    def get_arrival_predictions(self, line_id):
        return self._request("/line/{0}/arrivals".format(line_id))

    def _request(self, path, **kwargs):
        url = "https://api.tfl.gov.uk{path}?app_id={app_id}&app_key={app_key}".format(path=path, app_id=APP_ID, app_key=APP_KEY)
        r = requests.get(url, timeout=60)
        return r.json()

##############################################################################

class LineInfo:
    def __init__(self, api, id):
        self.id = id
        self.api = api

    @functools.lru_cache
    def get_stations(self, direction):
        r = self._get_line(direction)
        stations = OrderedDict()
        for stop in r['stopPointSequences'][0]['stopPoint']:
            stations[stop['id']] = (stop['name'], stop['lat'], stop['lon'])
        return stations

    @functools.lru_cache
    def path(self, direction):
        r = self._get_line(direction)
        assert len(r['lineStrings']) == 1
        assert len(json.loads(r['lineStrings'][0])) == 1
        return LineString(json.loads(r['lineStrings'][0])[0])

    @functools.lru_cache
    def _get_line(self, direction):
        return self.api.get_line(self.id, direction)

##############################################################################

class Bus:
    def __init__(self, id, line_id, line_info):
        self.id = id
        self.line_id = id
        self.line_info = line_info
        self.eta = XXX # TODO
        self.time_to_dest = XXX # TODO

    def update_estimate(self):
        # TODO

    def to_geojson_feature(self):
        return geojson.Feature(
            id=id,
            geometry=self._interpolated_position(),
            properties={
                'vehicle id': self.id,
                'route': self.line_id
            })

    def _interpolated_position(self):
        # TODO: what is bus_arrival?
        previous = self.line_info.previous_stop(bus_arrival)
        current = self.line_info.current_stop(bus_arrival)
        proportion = self.eta / self.time_to_dest

        pos = self._get_position(current, previous, proportion)
        pos = self.line_info.path().interpolate(
            self.line_info.path().project(pos, normalized=True),
            normalized=True
        )

    def _get_position(a, b, proportion):
        segment = LineString(((a[2], a[1]), (b[2], b[1])))
        return segment.interpolate(distance=proportion, normalized=True)





##############################################################################

class Line:
    def __init__(self, id):
        self.id = id
        self.buses = {}
        # TODO: get line info

    def update_from_api(self):
        # TODO: get updates from API
        predictions = XXX

        # TODO: propagate updates to individual buses (creating/deleting as necessary)

    def update_estimates(self):
        for bus in self.buses:
            bus.update_estimate()



def main_loop:
    for line in lines:
        if (t >= API_DT):
            line.update_from_api()

        line.update_estimates()
        line.send_geojson()

async def main_loop(app):
    all_states = {}
    for line_id in LINE_IDS:
        all_states[line_id] = initialise(line_id)

    t = 0
    while True:
        for line_id, line_state in all_states:
            if t >= API_DT:
                update_from_api(line_id, line_state)

            update_estimates(line_id, line_state)
            await send_geojson(line_id, line_state)

        if t >= API_DT:
            t -= API_DT
        t += ANIMATION_DT
        await asyncio.sleep(ANIMATION_DT)


async def websocket_handler(request):
    logging.info("Registering websocket connection")
    global websockets

    ws = web.WebSocketResponse()
    await ws.prepare(request)
    websockets.add(ws)

    async for msg in ws:
        pass

    logging.info("Unregistering websocket connection")
    websockets.remove(ws)

    return ws

async def start_background_tasks(app):
    app['main_loop'] = app.loop.create_task(main_loop(app))

async def cleanup_background_tasks(app):
    app['main_loop'].cancel()

async def status(request):
    return web.Response(text="Sweet")

if __name__ == "__main__":
    app = web.Application()
    app.on_startup.append(start_background_tasks)
    app.on_cleanup.append(cleanup_background_tasks)
    app.router.add_get('/healthcheck', status)
    app.router.add_get('/tayo', websocket_handler)
    web.run_app(app)
