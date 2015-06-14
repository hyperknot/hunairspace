import os
import pyproj
from shapely.geometry import Point, LineString, asShape
from shapely.geometry.polygon import Polygon
from .utils import read_json


def generate_circle(lon, lat, radius_meters):
    points = list()
    for dir in range(0, 360, 15):
        p = offset_point(lon, lat, radius_meters, dir)
        points.append(p)
    return Polygon(points)


def offset_point(p1_lon, p1_lat, distance_meters, direction_degrees=0):
    geod = pyproj.Geod(ellps='WGS84')
    p2_lon, p2_lat, _ = geod.fwd(p1_lon, p1_lat, direction_degrees, distance_meters)
    return p2_lon, p2_lat


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
    for i, section in enumerate(point_list):
        # LineString
        if type(section).__name__ == 'LineString':
            assert i != 0 and i != len(point_list) - 1
            point_start = Point(point_list[i - 1])
            point_end = Point(point_list[i + 1])

            line_section = calculate_border_between_points(point_start, point_end, section)
            new_point_list.extend(line_section)

        # normal point
        else:
            new_point_list.append(section)

    return new_point_list


def calculate_border_between_points(point_a, point_b, border):
    dir_sign = 1

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
        dir_sign *= -1

    coords = selected.coords

    # cutting start and endpoints
    coords = coords[1:-1]

    # swapping direction
    if dists != dists_sorted:
        dir_sign *= -1

    if dir_sign == -1:
        coords = coords[::-1]

    return coords


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
    border = border.simplify(0.001)

    assert border.coords[0] == border.coords[-1]
    return LineString(border)


def feet_to_meters(feet):
    feet_in_meters = 0.3048
    return int(feet * feet_in_meters)


def fl_to_meters(fl):
    feet_in_meters = 0.3048
    return int(fl * 100 * feet_in_meters)


# helper function for debugging
def visualize_geometries(_locals, names):
    import os
    import geojson
    from geojson import Feature, FeatureCollection
    from ..utils import write_file_contents, run_cmd

    features = [Feature(geometry=_locals[name],
                        properties={
                            'name': name,
                            'area': _locals[name].area})
                for name in names
                if _locals[name].area > 0]

    fc = FeatureCollection(features)

    write_file_contents('tmp.json', geojson.dumps(fc))
    run_cmd('geojsonio tmp.json')
    os.remove('tmp.json')


