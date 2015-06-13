import re
from shapely.geometry import LineString
from shapely.geometry.polygon import Polygon
from .geom import convert_dms_to_float, generate_circle, process_border, fl_to_meters, \
    feet_to_meters


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
    regex = r'^(\d{2,3})(\d{2})(\d{2}(?:.\d+)?)([NSWE])$'
    m = re.search(regex, dms_str.strip())
    assert len(m.groups()) == 4

    deg, min, sec, dir = m.groups()
    deg = int(deg)
    min = int(min)
    sec = float(sec)

    if dir.upper() in ['S', 'W']:
        sign = -1
    else:
        sign = 1

    return convert_dms_to_float(deg, min, sec, sign)


def process_circle(circle_str):
    regex = r'(\d+(?:\.\d+)?) KM.*?(\d+[NS] \d+[EW])$'
    m = re.search(regex, circle_str.strip())
    assert len(m.groups()) == 2

    radius, center = m.groups()
    radius = float(radius)

    lon, lat = latlon_str_to_point(center)
    return generate_circle(lon, lat, radius * 1000)


# return meter, AGL bool
def process_altitude(alt_string):
    alt_string = alt_string.strip()

    if alt_string == 'GND':
        return 0, False

    regex_fl = r'^FL\ (\d+)$'
    m = re.search(regex_fl, alt_string)
    if m:
        feet = float(m.group(1))
        return fl_to_meters(feet), False

    regex_feet = r'^(\d[\d ]*) FT(?: ALT)?$'
    m = re.search(regex_feet, alt_string)
    if m:
        feet = float(m.group(1).replace(' ', ''))
        return feet_to_meters(feet), False

    regex_feet_agl = r'^(\d[\d ]*) FT AGL$'
    m = re.search(regex_feet_agl, alt_string)
    if m:
        feet = float(m.group(1).replace(' ', ''))
        return feet_to_meters(feet), True

    raise ValueError('cannot parse alt string:', alt_string)
