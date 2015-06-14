import os
import geojson
from geojson import Feature, FeatureCollection
from .utils import read_json, delete_dir, ensure_dir, write_file_contents
from .config import json_dir, geojson_dir


def make_features(border, process_raw_geometry):
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

            properties = {k: v for k, v in d.iteritems() if not k.startswith('geom')}
            feature = Feature(geometry=geom, id=1, properties=properties)

            features.append(feature)

    return features


def write_geojsons(features):
    classes = {f['properties']['class'] for f in features}

    for cl in classes:
        fc = FeatureCollection([f for f in features if f['properties']['class'] == cl])
        write_file_contents(os.path.join(geojson_dir, '{}.geojson'.format(cl)), geojson.dumps(fc))


