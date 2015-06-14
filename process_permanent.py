#!/usr/bin/env python

from pgairspace.config import geojson_dir, all_geojson
from pgairspace.utils import read_json, write_json, delete_dir, ensure_dir
from pgairspace.geom import load_border
from pgairspace.features import make_features, write_geojsons
from pgairspace.hun.permanent import process_chapters, process_airports
from pgairspace.hun.geom import process_raw_geometry
from pgairspace.hun.features import process_altitudes, process_g_airspace


# # download and process to json
# process_chapters()
# process_airports()

# # geometry
delete_dir(geojson_dir)
ensure_dir(geojson_dir)

border = load_border('hungary.json')
features = make_features(border, process_raw_geometry)
write_json(all_geojson, features)

# features
features = read_json(all_geojson)
process_altitudes(features)
process_g_airspace(features)

# write_json('g.geojson', g)
write_geojsons(features)
