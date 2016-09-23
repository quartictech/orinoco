from flask import Flask
from flask import request
import csv
import geojson
app = Flask(__name__)

def prepare_geojson(values):
    pass

@app.route('/gps', methods=['POST'])
def post_data():
    data = request.data.decode('utf-8')
    test = csv.reader(data.split('\n'))
    for r in test:
        print(r)
    return ('', 200)
