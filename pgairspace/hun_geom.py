import re
from .geom import convert_dms_to_float, generate_circle


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

