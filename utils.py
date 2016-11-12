import xml.etree.ElementTree as ET
import geojson
import csv

OWNERS = {
    '8676860225183181212': 'Alex',
    '0F781721-29A9-48C5-A24E-62877E56FCB3': 'Arlo'
}

# See http://www.btraced.com/Btraced%20Protocol%20v1.1.4.pdf for the Btraced protocol

def prepare_feature(v):
    loc = geojson.Point([float(v['lon']), float(v['lat'])])
    nice_id = OWNERS.get(v['devid'], 'unknown')
    p = {
        'name':         nice_id,
        'time':         int(v['time']),
        'pid':          v['pointid'],
        'timestamp':    round(float(v['date'])),
        'speed':        float(v['speed']),
        'vaccuracy':    float(v['vaccu']),
        'battery':      float(v['bat']),
        'altitude':     float(v['altitude'])
    } #haccu not appearing for some reason
    return geojson.Feature(geometry=loc, properties=p, id=nice_id)

def prepare_feature_collection(values):
    feature_list = []
    for v in values:
        feature_list.append(prepare_feature(v))
    return geojson.FeatureCollection(feature_list)

def parse_csv(csv_data):
    data = csv.reader(csv_data.split('\n'))
    next(data)
    features = []
    for r in data:
        if (len(r) == 0):
            continue
        pos_info = {
            'tripid': r[5],
            'pointid': r[11],
            'time': r[8],
            'devid': r[3],
            'date': r[12],
            'lat': r[13],
            'lon': r[14],
            'speed': r[15],
            'haccu': r[17],
            'vaccu': r[18],
            'bat': r[19],
            'altitude': r[20]
        }
        features.append(pos_info)
    return features

def prepare_return(features):
    point_ids = []
    for f in features:
        point_ids.append(int(f['pointid']))
    return {
        'id':       0,
        'tripid':   int(features[0]['tripid']),
        'points':   point_ids,
        'valid':    True
    }

def prepare_error_return(features):
    return {
        'id':       901,
        'tripid':   int(features[0]['tripid']),
        'points':   [],
        'valid':    True,
        'error':    True,
        'message':  'Error hitting Weyl'
    }

def parse_xml(xml):
    pos_info = {}
    root = ET.fromstring(xml)
    devId = root.find('devId')
    pos_info['devid'] = devId.text
    travel = root.find('travel')
    for child in travel:
        if child.tag == 'time':
            pos_info['time'] = child.text
        if child.tag == 'id':
            pos_info['tripid'] = child.text
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
                elif child.tag == 'haccu':
                    pos_info['haccu'] = child.text
                elif child.tag == 'bat':
                    pos_info['bat'] = child.text
                elif child.tag == 'altitude':
                    pos_info['altitude'] = child.text
    return pos_info
