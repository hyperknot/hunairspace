#!/usr/bin/env python

from shapely.geometry.polygon import Polygon
from pgairspace.utils import pp # noqa
from pgairspace.hun_aip import process_chapters, process_airports
from pgairspace.hun_geom import latlon_str_to_point, process_circle
from pgairspace.geom import plot_polygon

process_chapters()
process_airports()



from pgairspace.hun_aip import process_chapter


data = process_chapter('5.1')




def process_geometry(data):
    geom_raw = data['geom_raw']
    geom_split = [p.strip() for p in geom_raw.split('-')]

    points = list()
    for s in geom_split:
        if 'along border' in s:
            first, _ = s.split('along border')
            points.append(latlon_str_to_point(first))
            # points.append('border')

        elif s.startswith('A circle'):
            assert len(geom_split) == 1
            data['geom'] = process_circle(s)
            return data

        else:
            points.append(latlon_str_to_point(s))

    assert points[0] == points[-1]

    data['geom'] = Polygon(points)
    return data






# for d in data:
    # g = process_geometry(d)



d = data[0]
g = process_geometry(d)
plot_polygon(g['geom'])

