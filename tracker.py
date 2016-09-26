from flask import Flask
from flask import request
from flask import jsonify
import requests
from pprint import pprint
import math
import csv
import json
import geojson
import utils


# See http://www.btraced.com/Btraced%20Protocol%20v1.1.4.pdf for the Btraced protocol

#janky as balls - should possibly be argparse
USE_PROXY = True
if USE_PROXY:
    apiRoot = 'http://localhost:6666/api'

app = Flask(__name__)



@app.route('/gps', methods=['POST'])
def post_data():
    data = request.data.decode('utf-8')
    if request.headers.get('User-Agent') == 'androidSync/1.0':
        features = [utils.parse_xml(data)]
    else:
        features = utils.parse_csv(data)

    geoj = utils.prepare_geojson_array(features)
    pprint(geoj)

    return_blob = utils.prepare_return(features)

    if USE_PROXY:
        r = requests.post("{}/layer/live/{}".format(apiRoot, "12345678"), json={
            'name': 'Quartic tracking',
            'description': 'Quartic phones',
            'featureCollection': geoj
        })
        print(r)
        if (math.floor(r.status_code / 100) != 2):
            return_blob = utils.prepare_error_return(features)

    print(return_blob)
    return jsonify(return_blob)
