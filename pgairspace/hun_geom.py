import re
from .geom import convert_dms_to_float, generate_circle


def latlon_str_to_point(latlon_str):
    lat_str, lon_str = latlon_str.strip().split(' ')
    lat = process_dms_str(lat_str)
    lon = process_dms_str(lon_str)

    return lon, lat


def process_dms_str(dms_str):
    if len(dms_str) == 7:
        dms_str = '0' + dms_str
    assert len(dms_str) == 8

    deg = int(dms_str[:3])
    min = int(dms_str[3:5])
    sec = int(dms_str[5:7])
    dir = dms_str[7]

    if dir.upper() in ['S', 'W']:
        sign = -1
    else:
        sign = 1

    return convert_dms_to_float(deg, min, sec, sign)


def process_circle(circle_str):
    circle_str = circle_str.strip()
    regex_str = r'A\ circle\ with\ (?:a\ )?radius\ of\ (\d+(?:\.\d+)?) KM\ centred\ on\ (\d+[NS]\ \d+[EW])'
    regex = re.compile(regex_str)

    match = re.match(regex, circle_str)
    assert match

    radius, center = match.groups()
    radius = float(radius)

    lat, lon = latlon_str_to_point(center)
    return generate_circle(lat, lon, radius * 1000)


