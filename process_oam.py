#!/usr/bin/env python

import xml.etree.ElementTree as ET
from hunairspace.utils import write_json
import json

feet_in_meters = 0.3048


def make_dict(tags):
    data = dict()
    for tag in tags:
        k = tag.get('k')
        v = tag.get('v')
        data[k] = v
    return data


def process_nodes(nodes):
    data = dict()
    for node in nodes:
        id = node.attrib['id']
        lat = node.attrib['lat']
        lon = node.attrib['lon']
        data[id] = {
            'lat': float(lat),
            'lon': float(lon),
        }
    return data


def make_geometry(nds):
    if nds[0].attrib['ref'] != nds[-1].attrib['ref']:
        print 'not closed geometry'
        return

    geometry = list()
    for nd in nds:
        id = nd.attrib['ref']
        geometry.append(nodes[id])
    return geometry


def get_lower_upper(raw, data):
    misc = None

    l = float(raw['height:lower'])
    lc = raw['height:lower:class']
    lu = raw['height:lower:unit']

    u = float(raw['height:upper'])
    uc = raw['height:upper:class']
    uu = raw['height:upper:unit']

    if lu == 'ft':
        l *= feet_in_meters
    if uu == 'ft':
        u *= feet_in_meters

    if lu == 'fl':
        l *= feet_in_meters * 100

    if uu == 'fl':
        u *= feet_in_meters * 100

    if lc == 'agl' and l != 0:
        info = additional_info[data['name']]
        l += info['elev']
        misc = info['misc']

    if uc == 'agl':
        info = additional_info[data['name']]
        u += info['elev']
        misc = info['misc']

    # overrides
    if data['name'] in additional_info:
        info = additional_info[data['name']]
        if 'upper' in info:
            u = info['upper']
        if 'lower' in info:
            l = info['lower']

    return int(l), int(u), misc


def rename_airspace(data):
    for string in rename_strings:
        data['name'] = data['name'].replace(string[0], string[1])
    return data



def process_ways(ways):
    processed_list = list()

    for way in ways:
        # raw
        tags = way.findall('tag')
        raw = make_dict(tags)

        # filtering
        if 'airspace' not in raw:
            continue

        # geometry
        nds = way.findall('nd')
        geometry = make_geometry(nds)

        # clean data
        data = dict()

        # name
        if 'icao' in raw:
            data['name'] = raw['icao']
            data['desc'] = raw['name']
        else:
            data['name'] = raw['name']
            data['desc'] = ''

        if data['name'] in exclude_names:
            continue

        # type
        if 'airspace:type' in raw:
            data['type'] = raw['airspace:type']
        else:
            data['type'] = 'other'

        if data['type'] in exclude_types:
            continue

        # type list
        airtypes.add(data['type'])

        # other
        data['note'] = raw.get('remarks', '')

        # agl elevation
        data['lower'], data['upper'], misc = get_lower_upper(raw, data)
        if data['lower'] >= data['upper']:
            print 'lower >= upper: ', data
        if misc:
            data['desc'] = misc

        data = rename_airspace(data)


        airspace = {
            'raw': raw,
            'geometry': geometry,
            'data': data,
        }

        processed_list.append(airspace)

    return processed_list


def airspace_to_geojson(airspace):
    geometry = {
        'type': 'Polygon',
        'coordinates': [[[g['lon'], g['lat']] for g in airspace['geometry']]],
    }

    geojson = {
        'type': 'Feature',
        'geometry': geometry,
        'properties': airspace['data']
    }

    return geojson



def make_geojson(airspaces, airtype):
    features = [airspace_to_geojson(airspace) for airspace in airspaces
        if airspace['data']['type'] == airtype]

    geojson = {
        'type': 'FeatureCollection',
        'features': features
    }

    return geojson


exclude_types = ['B']

exclude_names = ['BUDAPEST FIR', 'BUDAPEST CTA',
    'LHSG2V', 'LHSG24', 'LHSG25', 'LHSG30', 'LHSG1', 'FERTOSZENTMIKLOS TIZ']

additional_info = {
    'KOSICE TMA 2': {
        'elev': 300,
        'misc': 'ground +305 m'
    },
    'LHSG2S': {
        'upper': 3500 * feet_in_meters,
    },
    'LHSG3': {
        'upper': 4500 * feet_in_meters,
    },
    'LHSG10': {
        'upper': 4500 * feet_in_meters,
    },
    'LHSG20': {
        'upper': 2000 * feet_in_meters,
    },
    'LHSG20A': {
        'upper': 2000 * feet_in_meters,
        'lower': 0,
    },
    'LHSG21': {
        'upper': 2500 * feet_in_meters,
    },
    'LHSG22': {
        'upper': 3000 * feet_in_meters,
    },
    'LHSG23': {
        'upper': 6500 * feet_in_meters,
    },
}
rename_strings = [
    ('KECSKEMET', 'LHKE'),
    ('SZOLNOK', 'LHSN'),
    ('PAPA', 'LHPA'),
    ('LHTRA', 'TRA '),
    ('LHD', 'LH-D')
]

airtypes = set()

tree = ET.parse('oam-hungary.xml')
root = tree.getroot()

nodes_xml = root.findall('node')
nodes = process_nodes(nodes_xml)

ways = root.findall('way')
airspaces = process_ways(ways)
write_json('hun.json', airspaces)

for airtype in airtypes:
    geojson = make_geojson(airspaces, airtype)
    write_json('html/{}.geojson'.format(airtype), geojson)

