import geojson
import json
import os

from geojson import Feature, FeatureCollection

from .config import json_dir, geojson_dir
from .utils import read_json, write_file_contents
from .geom import sort_geojson


def make_features(border, process_raw_geometry):
    print '---\nMaking features'

    features = list()

    for filename in os.listdir(json_dir):
        json_file = os.path.join(json_dir, filename)
        data = read_json(json_file)

        for d in data:
            if d['geom_raw'] == 'Lateral limits as for Budapest FIR':  # TODO
                continue

            if d['geom_raw'] == 'along border  AUSTRIA_HUNGARY then a clokwise arc radius  centered on 7.6 KM 474052N 0164600E':  # TODO
                continue

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
        geojson_data = sort_geojson(json.loads(geojson.dumps(fc)))
        body = json.dumps(geojson_data, ensure_ascii=False, indent=2, sort_keys=True)

        write_file_contents(os.path.join(geojson_dir, '{}.geojson'.format(cl)), body)



