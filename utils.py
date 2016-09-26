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

root = ET.fromstring(test_xml)
for child in root:
    print(child.tag, child.text)
travel = root.find('travel')
for child in travel:
    print(child.tag, child.text)
    if child.tag == 'point':
        point = child
        for child in point:
            print(child.tag, child.text)

def parse_xml(xml):
    root = ET.fromstring(xml)
    travel = root.find('travel')
    for child in travel:
        print(child.tag)
