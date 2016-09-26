import xml.etree.ElementTree as ET

def prepare_geojson(value_list):
    feature_list = []
    for values in value_list:
        loc = geojson.Point([float(values[4]), float(values[3])])
        p = {'time' : int(values[0]), 'pid' : values[1], 'timestamp' : round(float(values[2])),
                'speed' : float(values[5]), 'accuracy' : float(values[6]), 'vaccuracy' : float(values[7]),
                'battery' : float(values[8]), 'altitude' : float(values[9])}
        f = geojson.Feature(geometry=loc, properties=p, id=values[1])
        feature_list.append(f)
    return geojson.FeatureCollection(feature_list)

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

print(parse_xml(test_xml))
