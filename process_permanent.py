#!/usr/bin/env python

from pgairspace.config import geojson_dir, geom_json
from pgairspace.utils import read_json, write_json, delete_dir, ensure_dir
from pgairspace.geom import load_border
from pgairspace.features import make_features, write_geojsons
from pgairspace.hun.permanent import process_chapters, process_airports
from pgairspace.hun.geom import process_raw_geometry
from pgairspace.hun.features import process_altitudes, process_g_airspace, subtract_tma_g


# # # download and process to json
# process_chapters()
# process_airports()

# # # geometry
# border = load_border('hungary.json')
# features = make_features(border, process_raw_geometry)
# write_json(geom_json, features)

# features
features = read_json(geom_json)
process_altitudes(features)
process_g_airspace(features)
subtract_tma_g(features)

delete_dir(geojson_dir)
ensure_dir(geojson_dir)
write_geojsons(features)
