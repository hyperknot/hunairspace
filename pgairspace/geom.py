import pyproj
import matplotlib.pyplot as plt
from shapely.geometry.polygon import Polygon


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
    x, y = polygon.exterior.xy
    plt.plot(x, y)
    plt.show()


def convert_dms_to_float(deg, min, sec, sign=1):
    return sign * deg + min / 60. + sec / 3600.
