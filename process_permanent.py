#!/usr/bin/env python

from shapely.geometry.polygon import Polygon
from pgairspace.utils import write_file_contents, read_json, delete_dir, ensure_dir
from pgairspace.hun_permanent import process_chapters, process_airports, json_dir
from pgairspace.hun_geom import latlon_str_to_point, process_circle
from pgairspace.geom import process_border, load_border


process_chapters()
process_airports()
border = load_border('hungary.json')



def process_raw_geometry(geom_raw, border):
    geom_raw_split = [p.strip() for p in geom_raw.split('-')]

    point_list = list()

    for s in geom_raw_split:
        # process circle separately
        if s.startswith('A circle'):
            assert len(geom_raw_split) == 1
            return process_circle(s)

        if 'along border' in s:
            first, _ = s.split('along border')
            point_list.append(latlon_str_to_point(first))
            point_list.append('border')

        elif 'then a clockwise arc' in s:
            first, _ = s.split('then a clockwise arc')
            point_list.append(latlon_str_to_point(first))
            # point_list.append('border')

        else:
            point_list.append(latlon_str_to_point(s))

    assert point_list[0] == point_list[-1]

    point_list_border = process_border(point_list, border)
    return Polygon(point_list_border)



import os
import geojson
from geojson import Feature, FeatureCollection

features = list()
classes = set()

delete_dir('geojson')
ensure_dir('geojson')

for filename in os.listdir(json_dir):
    json_file = os.path.join(json_dir, filename)
    data = read_json(json_file)

    for d in data:
        cl = d['class']
        classes.add(cl)

        geom = process_raw_geometry(d['geom_raw'], border)
        properties = {k: v for k, v in d.iteritems() if not k.startswith('geom')}
        feature = Feature(geometry=geom, id=1, properties=properties)

        features.append(feature)

for cl in classes:
    fc = FeatureCollection([f for f in features if f['properties']['class'] == cl])
    write_file_contents('geojson/{}.geojson'.format(cl), geojson.dumps(fc))


