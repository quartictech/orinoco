import xml.etree.ElementTree as ET
import geojson
from flask import jsonify

def prepare_geojson(values):
    feature_list = []
    for v in values:
        loc = geojson.Point([float(v['lon']), float(v['lat'])])
        p = {'time' : int(v['time']), 'pid' : v['pointid'], 'timestamp' : round(float(v['date'])),
                'speed' : float(v['speed']), 'accuracy' : float(v['haccu']), 'vaccuracy' : float(v['vaccu']),
                'battery' : float(v['bat']), 'altitude' : float(v['altitude'])}
        f = geojson.Feature(geometry=loc, properties=p, id=v['pointid'])
        feature_list.append(f)
    return geojson.FeatureCollection(feature_list)

def parse_csv(csv_data):
    data = csv.reader(csv.data.split('\n'))
    next(data)
    features = []
    for r in data:
        if (len(r) == 0):
            continue
        #POINTID TIME DEVID DATE LATITUDE LONGITUDE SPEED HACCU VACCU BAT ALTITUDE
        pos_info = {'tripid' : r[5], 'pointid' : r[11], 'time' : r[8], 'devid' : r[3], 'date' : r[12],
                    'lat' : r[13], 'lon' : r[14], 'speed' : r[15],
                    'haccu' : r[17], 'vaccu' : r[18], 'bat' : r[19], 'altitude' : r[20]}
        point_ids.append(int(r[10]))
        trip_id=int(r[5])
        features.append(pos_info)
        return features

def prepare_return(features):
    point_ids = []
    for f in features:
        point_ids.append(f['pointid'])
    return jsonify(
        id=0,
        tripid = features[0]['tripid'], #all points should have the same tripid
        points = point_ids,
        valid = True
    )


def parse_xml(xml):
    pos_info = {}
    root = ET.fromstring(xml)
    devId = root.find('devId')
    pos_info['devid'] = devId.text
    travel = root.find('travel')
    for child in travel:
        if child.tag == 'time':
            pos_info['time'] = child.text
        if child.tag == 'point':
            point = child
            for child in point:
                if child.tag == 'id':
                    pos_info['pointid'] = child.text
                elif child.tag == 'date':
                    pos_info['date'] = child.text
                elif child.tag == 'lat':
                    pos_info['lat'] = child.text
                elif child.tag == 'lon':
                    pos_info['lon'] = child.text
                elif child.tag == 'speed':
                    pos_info['speed'] = child.text
                elif child.tag == 'haccu':
                    pos_info['speed'] = child.text
                elif child.tag == 'vaccu':
                    pos_info['vaccu'] = child.text
                elif child.tag == 'bat':
                    pos_info['bat'] = child.text
                elif child.tag == 'altitude':
                    pos_info['altitude'] = child.text
    return pos_info

if __name__ == "__main__":

    test_xml = b"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
    <bwiredtravel>
        <model>Android</model>
        <devId>8676860225183181212</devId>
        <username/>
        <password/>
        <timeOffset>3600</timeOffset>
        <travel>
            <id>1</id>
            <getTripUrl>1</getTripUrl>
            <description>15/09/2016 14:51_trip</description>
            <length>0.00</length>
            <time>876</time>
            <tpoints>22</tpoints>
            <uplpoints>0</uplpoints>
            <point>
                <id>22</id>
                <date>1473951960.157</date>
                <lat>51.5054379</lat>
                <lon>-0.0223121</lon>
                <speed>-1.0</speed>
                <course>-1.00</course>
                <haccu>50.0</haccu>
                <bat>0.58</bat>
                <vaccu>-1.0</vaccu>
                <altitude>0.00</altitude>
                <continous>1</continous>
                <tdist>0.00</tdist>
                <rdist>0.00</rdist>
                <ttime>876</ttime>
            </point>
        </travel>
    </bwiredtravel>"""


    print(parse_xml(test_xml))
