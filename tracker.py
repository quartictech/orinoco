from flask import Flask
from flask import request
from flask import jsonify
import requests
from pprint import pprint
import csv
import json
import geojson
import utils


# See http://www.btraced.com/Btraced%20Protocol%20v1.1.4.pdf for the Btraced protocol

#janky as balls - should possibly be argparse
USE_PROXY = False
if USE_PROXY:
    apiRoot = 'http://localhost:6666/api'

    r = requests.put("{}/layer/live".format(apiRoot), json={'name': 'Arlo', 'description': "Arlo's phone"})
    layerId = r.json()


app = Flask(__name__)



@app.route('/gps', methods=['POST'])
def post_data():
    data = request.data.decode('utf-8')
    if request.headers.get('User-Agent') == 'androidSync/1.0':
        features = utils.parse_xml(data)
        geoj = utils.prepare_geojson_value(features)
        return_blob = utils.prepare_return_from_xml(features)
    else:
        features = utils.parse_csv(data)
        geoj = utils.prepare_geojson(features)
        return_blob = utils.prepare_return(features)

    pprint(geoj)

    if USE_PROXY:
        r = requests.post("{}/layer/live/{}".format(apiRoot, layerId), json=geoj)
        print(r)
        # TODO: check that we got a 2xx response

    print(return_blob)

    return jsonify(return_blob)
