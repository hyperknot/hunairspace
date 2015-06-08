#!/usr/bin/env python

from pgairspace.hun_permanent import process_chapters, process_airports, json_dir
from pgairspace.geom import load_border
from pgairspace.hun_geom import process_raw_geometry
from pgairspace.features import make_features, write_geojsons


process_chapters()
process_airports()
border = load_border('hungary.json')
features = make_features(json_dir, border, process_raw_geometry)
write_geojsons(features, 'geojson')
