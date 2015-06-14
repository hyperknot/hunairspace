#!/usr/bin/env python

from pgairspace.geom import load_border
from pgairspace.features import make_features, write_geojsons
from pgairspace.hun.permanent import process_chapters, process_airports
from pgairspace.hun.geom import process_raw_geometry
from pgairspace.hun.features import process_altitudes, process_g_airspace


# download online -> json and process
# process_chapters()
# process_airports()

# process local json
border = load_border('hungary.json')
features = make_features(border, process_raw_geometry)

# process features
process_altitudes(features)
# process_g_airspace(features)

write_geojsons(features)
