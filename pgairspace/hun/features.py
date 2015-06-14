import re
from ..geom import fl_to_meters, feet_to_meters


def process_altitudes(features):
    for feature in features:
        d = feature['properties']

        upper, upper_agl = process_altitude(d['upper_raw'])
        lower, lower_agl = process_altitude(d['lower_raw'])

        if upper <= lower:
            raise ValueError('upper <= lower: ', upper, lower)

        d['upper'] = upper
        d['lower'] = lower

    return features


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


def process_g_airspace(features):
    for feature in features:
        print feature['note']
