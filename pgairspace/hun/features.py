import re
from copy import deepcopy
from geojson import Feature
from shapely.geometry import asShape
from ..geom import fl_to_meters, feet_to_meters


def process_altitudes(features):
    for feature in features:
        d = feature['properties']

        d['upper'], d['upper_agl'] = process_altitude(d['upper_raw'])
        d['lower'], d['lower_agl'] = process_altitude(d['lower_raw'])

        if d['upper'] <= d['lower']:
            raise ValueError('upper <= lower: ', d['upper'], d['lower'])


# return meter, AGL bool
def process_altitude(alt_string):
    alt_string = alt_string.strip()

    if alt_string == 'GND':
        return 0, False

    regex_fl = r'^FL\ (\d+)$'
    m = re.search(regex_fl, alt_string)
    if m:
        feet = float(m.group(1))
        return fl_to_meters(feet), False

    regex_feet = r'^(\d[\d ]*) FT(?: ALT)?$'
    m = re.search(regex_feet, alt_string)
    if m:
        feet = float(m.group(1).replace(' ', ''))
        return feet_to_meters(feet), False

    regex_feet_agl = r'^(\d[\d ]*) FT AGL$'
    m = re.search(regex_feet_agl, alt_string)
    if m:
        feet = float(m.group(1).replace(' ', ''))
        return feet_to_meters(feet), True

    raise ValueError('cannot parse alt string:', alt_string)


def process_g_airspace(features):
    g_pg = dict()

    for feature in features:
        d = feature['properties']

        if d['class'] != 'G':
            continue

        if d['name'].startswith('LHSG2V'):
            continue

        if 'notes' in d:
            regex = r'Above (\d+) FT AMSL prior'
            m = re.search(regex, d['notes'])
            if m:
                new_feature = deepcopy(feature)
                nd = new_feature['properties']
                nd['upper'] = feet_to_meters(float(m.group(1)))
                nd['lower'] = 0
                nd['upper_agl'] = nd['lower_agl'] = False
                nd['name'] = d['name'].split('/')[0].strip()[3:]
                nd.pop('notes')
                nd.pop('lower_raw')
                nd.pop('upper_raw')
                nd['class'] = 'G_PG'

                g_pg[nd['name']] = new_feature

    g20 = asShape(g_pg['G20']['geometry'])
    g20a = asShape(g_pg['G20A']['geometry'])

    g_pg['G20']['geometry'] = g20.union(g20a)
    g_pg['G20']['properties']['name'] = 'G20-G20A'
    g_pg.pop('G20A')

    features.extend(g_pg.values())



def subtract_tma_g(features):
    airspaces_tma = [deepcopy(f) for f in features if f['properties']['class'] == 'TMA']
    airspaces_gpg = [deepcopy(f) for f in features if f['properties']['class'] == 'G_PG']

    air_mix = list()

    for air_tma in airspaces_tma:
        if air_tma['properties']['lower'] >= 2895:
            continue

        air_tma['properties']['name'] = air_tma['properties']['name'].replace('BUDAPEST', '').strip()
        air_tma['properties']['class'] = 'TMA_G_PG'
        air_tma['properties']['fill'] = '#1a9f2e'

        for air_gpg in airspaces_gpg:
            air_intersection = mix_tma_g(air_tma, air_gpg)
            if air_intersection:
                air_mix.append(air_intersection)

    features.extend(airspaces_tma)
    features.extend(air_mix)


def mix_tma_g(air_tma, air_g):
    eps = 1e-4

    geom_tma = asShape(air_tma['geometry'])
    geom_g = asShape(air_g['geometry'])

    if geom_g.intersects(geom_tma):
        geom_tma_minus_g = geom_tma.difference(geom_g)
        geom_intersection = geom_g.intersection(geom_tma)
        # geom_g_minus_tma = geom_g.difference(geom_tma)

        if geom_intersection.area < eps:
            return

        if air_tma['properties']['lower'] >= air_g['properties']['upper']:
            return

        air_tma['geometry'] = geom_tma_minus_g

        air_intersection = Feature(
            geometry=geom_intersection,
            properties=deepcopy(air_tma['properties']))

        air_intersection['properties']['name'] = '{} - {}'.format(
            air_tma['properties']['name'], air_g['properties']['name'])

        air_intersection['properties']['lower'] = air_g['properties']['upper']
        del(air_intersection['properties']['lower_raw'])
        air_intersection['properties']['class'] = 'TMA_G_PG'
        air_intersection['properties']['fill'] = '#457aa3'

        return air_intersection




