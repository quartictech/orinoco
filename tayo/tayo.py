import argparse
import json
import itertools
import geojson
import logging
import asyncio

from collections import OrderedDict
from shapely.geometry import LineString
from aiohttp import ClientSession
from pprint import pprint

from orinoco import create_app


APP_ID = "860e7675"
APP_KEY = "1d36a20279e6ac727ddfdcaeba2e97ea"

API_DT = 10
ANIMATION_DT = 3
LINE_IDS = ["88", "15", "9"]

##############################################################################

class Api:
    def __init__(self):
        self.session = ClientSession()

    async def get_line(self, line_id, direction):
        return await self._request("/Line/{}/Route/Sequence/{}".format(line_id, direction))

    async def get_arrival_predictions(self, line_id):
        return await self._request("/line/{0}/arrivals".format(line_id))

    async def _request(self, path, **kwargs):
        url = "https://api.tfl.gov.uk{path}?app_id={app_id}&app_key={app_key}".format(path=path, app_id=APP_ID, app_key=APP_KEY)
        async with self.session.get(url, timeout=20) as r:
            r.raise_for_status()
            return await r.json()


##############################################################################

class StationInfo:
    def __init__(self, name, lat, lon):
        self.name = name
        self.lat = lat
        self.lon = lon

    def __str__(self):
        return self.name


##############################################################################

class LineInfo:
    @classmethod
    async def create(cls, api, id):
        self = LineInfo()
        self.id = id
        self.lines = {
            "inbound": await api.get_line(id, "inbound"),
            "outbound": await api.get_line(id, "outbound")
        }
        return self

    def stations(self, direction):
        r = self.lines[direction]
        stations = OrderedDict()
        logging.debug("--- {} ---".format(direction))
        for stop in r['stopPointSequences'][0]['stopPoint']:
            logging.debug(stop["name"])
            stations[stop['id']] = StationInfo(stop["name"], stop["lat"], stop["lon"])
        return stations

    def path(self, direction):
        r = self.lines[direction]
        assert len(r['lineStrings']) == 1
        assert len(json.loads(r['lineStrings'][0])) == 1
        return LineString(json.loads(r['lineStrings'][0])[0])


##############################################################################

class ArrivalInfo:
    def __init__(self, dest_id, direction, time_to_dest):
        self.dest_id = dest_id
        self.direction = direction
        self.time_to_dest = time_to_dest

    def __str__(self):
        return "[{}, {}, {}]".format(self.dest_id, self.direction, self.time_to_dest)


##############################################################################

class Bus:
    def __init__(self, id, line_info):
        self.id = id
        self.line_info = line_info
        self.arrival_info = ArrivalInfo(None, None, None)   # Dummy info so that update_estimate does the right thing first time through

    def update_estimate(self, new_arrival_info, dt):
        if new_arrival_info is None:
            new_arrival_info = self.arrival_info

        new_prediction = new_arrival_info.time_to_dest
        if new_arrival_info.dest_id != self.arrival_info.dest_id:
            self.leg_time = new_prediction  # The initial estimate of the journey time
            self.eta = new_prediction
        else:
            # Only update if the bus isn't slowing down
            if (new_prediction <= self.prev_prediction):
                self.eta = max(min(new_prediction, self.eta - dt), 0)

        self.prev_prediction = new_prediction
        self.arrival_info = new_arrival_info

    def to_geojson_feature(self):
        return geojson.Feature(
            id=self.id,
            geometry=self._interpolated_position(),
            properties={
                'vehicle id': self.id,
                'route': self.line_info.id,
                'next stop': self._current_stop().name
            })

    def _interpolated_position(self):
        logging.debug("[{}] {} ({} -> {})".format(self.id, self.arrival_info.direction, self._previous_stop(), self._current_stop()))

        previous = self._previous_stop()
        current = self._current_stop()
        proportion = self.eta / self.leg_time

        path = self.line_info.path(self.arrival_info.direction)
        return path.interpolate(
            path.project(
                self._get_position(current, previous, proportion),
                normalized=True),
            normalized=True)

    def _previous_stop(self):
        stations = self.line_info.stations(self.arrival_info.direction)
        try:
            next_index = list(stations.keys()).index(self.arrival_info.dest_id)
            return list(stations.values())[max(next_index-1, 0)]
        except:
            raise RuntimeError("Could not find station {}".format(self.arrival_info.dest_id)) from None

    def _current_stop(self):
        stations = self.line_info.stations(self.arrival_info.direction)
        try:
            return stations[self.arrival_info.dest_id]
        except:
            raise RuntimeError("Could not find station {}".format(self.arrival_info.dest_id)) from None

    def _get_position(self, a, b, proportion):
        segment = LineString(((a.lon, a.lat), (b.lon, b.lat)))
        return segment.interpolate(distance=proportion, normalized=True)


##############################################################################

class Line:
    @classmethod
    async def create(cls, api, id):
        self = Line()
        self.id = id
        self.api = api
        self.line_info = await LineInfo.create(api, id)
        self.buses = {}
        return self

    async def update_from_api(self):
        try:
            info_for_buses = await self._get_bus_info()
        except Exception as e:
            logging.exception("Could not get info from API for line {}".format(self.id))
            return

        for bus_id, bus_info in info_for_buses.items():
            if bus_id not in self.buses:
                self.buses[bus_id] = Bus(bus_id, self.line_info)

            self.buses[bus_id].update_estimate(bus_info, ANIMATION_DT)

        # Remove buses without new predictions
        self.buses = {k: v for k, v in self.buses.items() if k in info_for_buses.keys()}

    def update_by_extrapolating(self):
        for bus in self.buses.values():
            bus.update_estimate(None, ANIMATION_DT)

    def to_geojson_features(self):
        features = []
        for bus in self.buses.values():
            try:
                features.append(bus.to_geojson_feature())
            except Exception as e:
                logging.exception("Could not calculate position for bus {} on line {}".format(bus.id, self.id))
        return features

    async def _get_bus_info(self):
        # The API returns predictions multiple stops ahead for each bus, so we have to extract the nearest one per bus
        bus_info = {}
        for p in await self.api.get_arrival_predictions(self.id):
            bus_id = p["vehicleId"]
            bus_info[bus_id] = bus_info.get(bus_id, [])
            bus_info[bus_id].append(ArrivalInfo(p["naptanId"], p["direction"], p["timeToStation"]))

        return {bus_id: min(infos, key=lambda k: k.time_to_dest) for bus_id, infos in bus_info.items()}


##############################################################################

async def create_lines():
    api = Api()
    while True:
        try:
            lines = [await Line.create(api, id) for id in LINE_IDS]
            break
        except Exception as e:
            logging.exception("Could not retrieve line info")
    return lines

async def process_line(line, t):
    if (t >= API_DT):
        await line.update_from_api()
    else:
        line.update_by_extrapolating()
    return line.to_geojson_features()

async def main_loop():
    lines = await create_lines()

    t = API_DT
    while True:
        feature_lists = [await process_line(line, t) for line in lines]
        features = list(itertools.chain.from_iterable(feature_lists))

        logging.info("Processed {0} features".format(len(features)))
        yield {
            'timestamp' : 0,
            'featureCollection' : geojson.FeatureCollection(features)
        }

        if t >= API_DT:
            t -= API_DT
        t += ANIMATION_DT
        await asyncio.sleep(ANIMATION_DT)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(levelname)s [%(asctime)s] %(name)s: %(message)s')

    app = create_app("tayo", main_loop)
    app.run()
