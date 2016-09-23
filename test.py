from flask import Flask
from flask import request
import csv
import geojson
app = Flask(__name__)

def prepare_geojson(values):
    loc = geojson.Point([float(values[3]), float(values[4])])
    p = {'time' : int(values[0]), 'pid' : values[1], 'date' : values[2],
            'speed' : float(values[5]), 'accuracy' : float(values[6]), 'vaccuracy' : float(values[7]),
            'battery' : float(values[8]), 'altitude' : float(values[9])}
    f = geojson.Feature(geometry=loc, properties=p, id=values[1])
    return geojson.FeatureCollection(f)

@app.route('/gps', methods=['POST'])
def post_data():
    data = request.data.decode('utf-8')
    test = csv.reader(data.split('\n'))
    next(test)
    for r in test:
        if (len(r) == 0):
            continue
        #TIME POINTID DATE LATITUDE LONGITUDE SPEED HACCU VACCU BAT ALTITUDE
        pos_info = (r[8], r[11], r[12], r[13], r[14], r[15], r[17], r[18], r[19], r[20])
        geoj = prepare_geojson(pos_info)
        print(geoj)
    return ('', 200)
