import os
import re
import geojson
from geojson import Feature, FeatureCollection
from .utils import read_json, delete_dir, ensure_dir, write_file_contents


def make_features(json_dir, border, process_raw_geometry):
    features = list()

    for filename in os.listdir(json_dir):
        json_file = os.path.join(json_dir, filename)
        data = read_json(json_file)

        for d in data:
            geom = process_raw_geometry(d['geom_raw'], border)

            # making union when geom_raw_union is present
            if 'geom_raw_union' in d:
                geom_and = process_raw_geometry(d['geom_raw_union'], border)
                geom = geom.union(geom_and)

            process_altitude(d['upper_raw'])

            properties = {k: v for k, v in d.iteritems() if not k.startswith('geom')}
            feature = Feature(geometry=geom, id=1, properties=properties)

            features.append(feature)

    return features


def write_geojsons(features, dir):
    delete_dir(dir)
    ensure_dir(dir)

    classes = {f['properties']['class'] for f in features}

    for cl in classes:
        fc = FeatureCollection([f for f in features if f['properties']['class'] == cl])
        write_file_contents(os.path.join(dir, '{}.geojson'.format(cl)), geojson.dumps(fc))


def process_altitude(alt_string):
    regex_fl = r'FL\ (\d+)'
    m = re.match(regex_fl, alt_string)
    if m:
        print m.groups(0)

    print alt_string
