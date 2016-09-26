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
    features = utils.parse_csv(data)
    print(request.headers)
    geoj = utils.prepare_geojson(features)
    return_blob = utils.prepare_return(features)

    pprint(geoj)

    if USE_PROXY:
        r = requests.post("{}/layer/live/{}".format(apiRoot, layerId), json=geoj)
        print(r)
        # TODO: check that we got a 2xx response

    return_blob = utils.prepare_return(features)
    print(return_blob)

    return jsonify(return_blob)
