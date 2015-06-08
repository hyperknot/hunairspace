import re
from shapely.geometry import LineString
from shapely.geometry.polygon import Polygon
from .geom import convert_dms_to_float, generate_circle, process_border


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
            point_list.append(LineString(border))

        elif 'then a clockwise arc' in s:
            first, arc_str = s.split('then a clockwise arc')
            point_list.append(latlon_str_to_point(first))
            circle = process_circle(arc_str).exterior
            point_list.append(LineString(circle))

        else:
            point_list.append(latlon_str_to_point(s))

    assert point_list[0] == point_list[-1]

    point_list_border = process_border(point_list, border)
    return Polygon(point_list_border)



def latlon_str_to_point(latlon_str):
    lat_str, lon_str = latlon_str.strip().split(' ')
    lat = process_dms_str(lat_str)
    lon = process_dms_str(lon_str)

    return lon, lat


def process_dms_str(dms_str):
    regex = r'^(\d{2,3})(\d{2})(\d{2}(?:.\d+)?)([NSWE])'
    match = re.match(regex, dms_str.strip())
    assert len(match.groups()) == 4

    deg, min, sec, dir = match.groups()
    deg = int(deg)
    min = int(min)
    sec = float(sec)

    if dir.upper() in ['S', 'W']:
        sign = -1
    else:
        sign = 1

    return convert_dms_to_float(deg, min, sec, sign)


def process_circle(circle_str):
    regex = r'.*?(\d+(?:\.\d+)?)\ KM.*?(\d+[NS]\ \d+[EW])'
    match = re.match(regex, circle_str.strip())
    assert len(match.groups()) == 2

    radius, center = match.groups()
    radius = float(radius)

    lon, lat = latlon_str_to_point(center)
    return generate_circle(lon, lat, radius * 1000)

