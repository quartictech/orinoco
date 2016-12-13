import requests
import xml.etree.ElementTree as ET
from collections import defaultdict
from datetime import datetime

headers = { "Content-Type": "application/soap+xml; charset=utf-8" }
url = "http://energywatch.natgrid.co.uk/EDP-PublicUI/PublicPI/InstantaneousFlowWebService.asmx"
soap = """
<soap12:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap12="http://www.w3.org/2003/05/soap-envelope">
    <soap12:Body>
    <GetInstantaneousFlowData xmlns="http://www.NationalGrid.com/EDP/UI/" />
    </soap12:Body>
    </soap12:Envelope>
    """

def request_flows_data():
    r = requests.post(url, data = soap, headers=headers)
    return ET.fromstring(r.text)

def ns_tag(tag):
    return str( ET.QName('http://www.NationalGrid.com/EDP/BusinessEntities/Public', tag) )

def first(e):
    return list(e)[0]

def parse_dt(s):
    if not s:
        return None
    return datetime.strptime(s, "%Y-%m-%dT%H:%M:%S")

def get_text(e, t):
    tag = e.find(ns_tag(t))
    if tag is not None:
        return tag.text
    else:
        return None

def fetch_data():
    data = request_flows_data()

    data_result = first(first(first(data)))
    published_time = get_text(data_result, "PublishedTime")

    result = defaultdict(list)
    for obj in data.iter(ns_tag("EDPObjectBE")):
        object_name = obj.find(ns_tag("EDPObjectName")).text
        for item in obj.find(ns_tag("EnergyDataList")):
            applicable_at = parse_dt(get_text(item, "ApplicableAt"))
            flow_rate = get_text(item, "FlowRate")
            if not (applicable_at and flow_rate):
                continue
            result[object_name].append({
                "applicable_at": applicable_at,
                "flow_rate": flow_rate,
                "schedule_time": parse_dt(get_text(item, "ScheduleTime"))
            })
    return {
        "published_time": parse_dt(published_time),
        "data": result
    }
