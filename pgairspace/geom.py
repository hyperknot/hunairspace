import os
import pyproj
from shapely.geometry import Point, LineString, asShape
from shapely.geometry.polygon import Polygon
from .utils import read_json


def generate_circle(lat, lon, radius_meters):
    points = list()
    for dir in range(0, 360, 15):
        p = offset_point(lat, lon, radius_meters, dir)
        points.append(p)
    return Polygon(points)


def offset_point(p1_lat, p1_lon, distance_meters, direction_degrees=0):
    geod = pyproj.Geod(ellps='WGS84')
    p2_lon, p2_lat, _ = geod.fwd(p1_lon, p1_lat, direction_degrees, distance_meters)
    return p2_lat, p2_lon


def plot_polygon(polygon):
    import matplotlib.pyplot as plt

    x, y = polygon.exterior.xy
    plt.plot(x, y)
    plt.show()


def plot_line(line):
    import matplotlib.pyplot as plt

    x, y = line.xy
    plt.plot(x, y)
    plt.show()


def convert_dms_to_float(deg, min, sec, sign=1):
    return sign * deg + min / 60. + sec / 3600.


def process_border(point_list, border):
    new_point_list = list()
    for i, point in enumerate(point_list):
        if point == 'border':
            assert i != 0 and i != len(point_list) - 1
            point_start = Point(point_list[i - 1])
            point_end = Point(point_list[i + 1])
            border_section = calculate_border_between_points(point_start, point_end, border)
            new_point_list.extend(list(border_section.coords))
        else:
            new_point_list.append(point)

    return new_point_list


def calculate_border_between_points(point_a, point_b, border):
    dists = [border.project(p) for p in [point_a, point_b]]
    dists_sorted = sorted(dists)
    points = [border.interpolate(d) for d in dists_sorted]

    segment_a, segment_bc = cut_line(points[0], border)
    segment_b, segment_c = cut_line(points[1], segment_bc)

    segment_round = LineString(list(segment_c.coords) + list(segment_a.coords))

    # selecting shorter segment
    if segment_b.length < segment_round.length:
        selected = segment_b
    else:
        selected = segment_round

    # cutting start and end segments if != points
    eps = 1.2e-14
    coords = selected.coords
    line_start = Point(coords[0]).buffer(eps, resolution=1)
    line_end = Point(coords[-1]).buffer(eps, resolution=1)

    # if not line_start.contains(points[0]) and not line_start.contains(points[1]):
    if not line_start.contains(points[0]):
        coords = coords[1:]

    # if not line_end.contains(points[0]) and not line_end.contains(points[1]):
    if not line_end.contains(points[1]):
        coords = coords[:-1]

    # swapping if opposite direction is required
    if dists != dists_sorted:
        selected = LineString(selected.coords[::-1])

    # returning segment without endpoints
    return LineString(coords)


def cut_line(cut_point, line, eps_mult=1e2):
    dist = line.project(cut_point)
    point = line.interpolate(dist)
    eps = line.distance(point) * eps_mult

    coords = list(line.coords)

    if point.coords[0] in coords:
        i = coords.index(point.coords[0])

        if i == 0:
            return LineString(), line
        if i == len(coords) - 1:
            return line, LineString()

        start_segment = LineString(coords[:i + 1])
        end_segment = LineString(coords[i:])

        return start_segment, end_segment


    for i, p in enumerate(coords[:-1]):
        line_segment = LineString([coords[i], coords[i + 1]])
        line_segment_buffer = line_segment.buffer(eps, resolution=1)

        if line_segment_buffer.contains(point):
            start_segment = LineString(coords[:i + 1] + [point])
            end_segment = LineString([point] + coords[i + 1:])

            return start_segment, end_segment

    raise Exception('point not found in line, consider raising eps_mult')


def load_border(filename):
    border_json = read_json(os.path.join('data', 'borders', filename))
    border = asShape(border_json['geometries'][0]).exterior
    border = border.simplify(0.01)

    assert border.coords[0] == border.coords[-1]
    return LineString(border)

