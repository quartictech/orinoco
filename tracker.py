from flask import Flask
from flask import request
from flask import jsonify
import requests
from pprint import pprint
import csv
import json
import geojson


# See http://www.btraced.com/Btraced%20Protocol%20v1.1.4.pdf for the Btraced protocol

#janky as balls - should possibly be argparse
USE_PROXY = False
if USE_PROXY:
    apiRoot = 'http://localhost:6666/api'

    r = requests.put("{}/layer/live".format(apiRoot), json={'name': 'Arlo', 'description': "Arlo's phone"})
    layerId = r.json()


app = Flask(__name__)

def prepare_geojson(values):
    feature_list = []
    loc = geojson.Point([float(values['lon']), float(values['lat'])])
    p = {'time' : int(values['time']), 'pid' : values['pointid'], 'timestamp' : round(float(values['date'])),
            'speed' : float(values['speed']), 'accuracy' : float(values['haccu']), 'vaccuracy' : float(values['vaccu']),
            'battery' : float(values['bat']), 'altitude' : float(values['altitude'])}
    f = geojson.Feature(geometry=loc, properties=p, id=values['pointid'])
    feature_list.append(f)
    return geojson.FeatureCollection(feature_list)

@app.route('/gps', methods=['POST'])
def post_data():
    data = request.data.decode('utf-8')
    test = csv.reader(data.split('\n'))

    next(test)

    features = []

    point_ids = []
    trip_id = ''

    for r in test:
        pprint(r)

        if (len(r) == 0):
            continue
        #POINTID TIME DEVID DATE LATITUDE LONGITUDE SPEED HACCU VACCU BAT ALTITUDE
        pos_info = {'pointid' : r[11], 'time' : r[8], 'devid' : r[3], 'date' : r[12],
                    'lat' : r[13], 'lon' : r[14], 'speed' : r[15],
                    'haccu' : r[17], 'vaccu' : r[18], 'bat' : r[19], 'altitude' : r[20]}
        point_ids.append(int(r[11]))
        trip_id=int(r[5])
        features.append(pos_info)

    geoj = prepare_geojson(features)

    pprint(geoj)

    if USE_PROXY:
        r = requests.post("{}/layer/live/{}".format(apiRoot, layerId), json=geoj)
        print(r)
        # TODO: check that we got a 2xx response

    return_blob = jsonify(
            id=0,
            tripid=trip_id,
            points=point_ids,
            valid=True)

    return return_blob
