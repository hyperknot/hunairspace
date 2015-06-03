#!/usr/bin/env python

from shapely.geometry.polygon import Polygon, LinearRing, LineString
from shapely.geometry import Point
from pgairspace.utils import pp # noqa
from pgairspace.utils import read_json
from pgairspace.hun_aip import process_chapters, process_airports
from pgairspace.hun_geom import latlon_str_to_point, process_circle
from pgairspace.geom import plot_line

process_chapters()
process_airports()



from pgairspace.hun_aip import process_chapter


data = process_chapter('2.1')




def process_geometry(data):
    geom_raw = data['geom_raw']
    geom_split = [p.strip() for p in geom_raw.split('-')]

    points = list()
    for s in geom_split:
        if 'along border' in s:
            first, _ = s.split('along border')
            points.append(latlon_str_to_point(first))
            points.append('border')

        elif s.startswith('A circle'):
            assert len(geom_split) == 1
            data['geom'] = process_circle(s)
            return data

        else:
            points.append(latlon_str_to_point(s))

    assert points[0] == points[-1]

    return points

    data['geom'] = Polygon(points)
    return data



def process_border(points_with_border, border):
    for i, point in enumerate(points_with_border):
        # print i, point
        if point == 'border':
            assert i != 0 and i != len(points_with_border) - 1
            point_start = Point(points_with_border[i - 1])
            point_end = Point(points_with_border[i + 1])
            calculate_border_between_points(point_start, point_end, border)




def calculate_border_between_points(point_a, point_b, border):
    dists = sorted([border.project(p) for p in [point_a, point_b]])
    points = [border.interpolate(d) for d in dists]






def cut_line(cut_point, line, eps=1.2e-10):
    dist = line.project(cut_point)
    point = line.interpolate(dist)

    coords = list(border.coords)

    # if cut_point in coords

    for i, p in enumerate(coords[:-1]):
        line_segment = LineString([coords[i], coords[i + 1]])
        line_segment_buffer = line_segment.buffer(eps, resolution=1, cap_style=3)
        if line_segment_buffer.contains(point):
            start_segment = LineString(coords[:i] + [point])
            end_segment = LineString([point] + coords[i:])

            return start_segment, end_segment

    raise Exception('point not found in line, consider raising eps')




for d in data:
    g = process_geometry(d)
    if 'border' in g:
        b = g
        break

from shapely.geometry import asShape

border_json = read_json('data/borders/hungary.json')
border = asShape(border_json['geometries'][0]).exterior
process_border(b, border)

