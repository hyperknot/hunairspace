#!/usr/bin/env python

from shapely.geometry.polygon import Polygon
from pgairspace.utils import pp # noqa
from pgairspace.hun_aip import process_chapters, process_airports
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




from pgairspace.hun_aip import process_chapter
import os

chapters = [f.rstrip('.sjon') for f in os.listdir('data/aip/json')]


l = list()
for ch in chapters:
    if ch == 'airport':
        continue

    data = process_chapter(ch)
    for d in data:
        cl = d['class']
        if cl in ['TIZ']:
            continue
        # print cl

        g = process_raw_geometry(d['geom_raw'], border)
        l.append(g)


from geojson import GeometryCollection
gc = GeometryCollection(l)

print gc




# for d in data:



# plot_line(LineString(g_orig))
# plot_line(LineString(g_border))


# import geojson
# print geojson.dumps(LineString(g_border))
