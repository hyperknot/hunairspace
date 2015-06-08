import os
import requests
from bs4 import BeautifulSoup
from .utils import beautify_html, write_file_contents, pp, write_json, ensure_dir, \
    read_file_contents


def process_chapters():
    for chapter in chapters:
        data = process_chapter(chapter)
        write_json(os.path.join(json_dir, '{}.json'.format(chapter)), data)


def process_airports():
    ensure_dir(json_dir)

    data = list()
    for airport in airports:
        data.append(process_airport(airport))

    write_json(os.path.join(json_dir, 'airports.json'), data)


def process_chapter(chapter):
    ensure_dir(html_dir)
    ensure_dir(json_dir)

    download_chapter(chapter, html_dir)
    html_file = os.path.join(html_dir, '{}.html'.format(chapter))
    soup = BeautifulSoup(read_file_contents(html_file))
    data = chapters[chapter](soup, chapter)
    return data


def process_airport(airport):
    download_airport(airport, html_dir)
    html_file = os.path.join(html_dir, '{}.html'.format(airport))
    soup = BeautifulSoup(read_file_contents(html_file))
    data = parse_airport(soup, airport)
    return data


def download_chapter(chapter, dir):
    url_template = 'http://ais.hungarocontrol.hu/aip/{version}/{version}-AIRAC/html/eAIP/LH-ENR-{chapter}-en-HU.html'

    url = url_template.format(version=version, chapter=chapter)
    html_file = os.path.join(dir, '{}.html'.format(chapter))
    if os.path.isfile(html_file):
        return
    print html_file
    r = requests.get(url)
    if r.ok:
        html = beautify_html(r.text)
        write_file_contents(html_file, html)



def download_airport(airport, dir):
    url_template = 'http://ais.hungarocontrol.hu/aip/{version}/{version}-AIRAC/html/eAIP/LH-AD-2.{airport}-en-HU.html'

    url = url_template.format(version=version, airport=airport)
    html_file = os.path.join(dir, '{}.html'.format(airport))
    if os.path.isfile(html_file):
        return
    print html_file
    r = requests.get(url)
    if r.ok:
        html = beautify_html(r.text)
        write_file_contents(html_file, html)



def parse_2(soup, _):
    filter_text = ['ALT', 'RUTOL AREA']

    data = list()

    tds = soup.find_all('td')

    for td in tds:
        if any([t in td.text for t in filter_text]):
            data.append(parse_2_td(td))
    return data


def parse_2_td(td):
    parts = [l.strip() for l in td.text.splitlines() if l.strip()]
    data = dict()
    data['name'] = parts[0]
    data['geom_raw'] = parts[1]
    data['upper_raw'] = parts[2]
    data['lower_raw'] = parts[3]
    if len(parts) == 5:
        data['class'] = parts[4]
    if len(parts) > 5:
        data['geom_raw_and'] = parts[5]
        assert parts[6] == data['upper_raw']
        assert parts[7] == data['lower_raw']
    if 'class' not in data:
        data['class'] = get_class_from_name(data['name'])
    return data


def parse_5(soup, chapter):
    data = list()

    h4s = soup.find_all('h4')
    if not h4s:
        h4s = soup.find_all('h3')

    for h4 in h4s:
        title = [l.strip() for l in h4.text.splitlines() if l.strip()][1]
        table = h4.find_next('table')
        if not table:
            continue
        data += parse_5_table(table, title, chapter)

    return data


def parse_5_table(table, title, chapter):
    class_lookup = {
        'Prohibited Areas': 'P',
        'Restricted Areas': 'R',
        'Danger Areas': 'D',
        'Temporary Restricted Areas': 'TRA',
        'Aerobatics area': 'SA',
        'Glider areas': 'G',
        'Drop zones': 'SA',
        'BIRD MIGRATION AND AREAS WITH SENSITIVE FAUNA': 'B'
    }

    data = list()

    trs = table.find_all('tr')
    for tr in trs:
        if chapter == '5.1':
            airspace = parse_5126_tr(tr)
        if chapter == '5.2':
            airspace = parse_5126_tr(tr)
        if chapter == '5.5':
            airspace = parse_55_tr(tr)
        if chapter == '5.6':
            airspace = parse_5126_tr(tr)
        if not airspace:
            continue
        airspace['class'] = class_lookup[title]
        data.append(airspace)
    return data


def parse_5126_tr(tr):
    tds = tr.find_all('td')
    if len(tds) != 3:
        return

    data = dict()
    for i, td in enumerate(tds):
        parts = [l.strip() for l in td.text.splitlines() if l.strip()]
        if i == 0:
            assert len(parts) == 2
            data['name'] = parts[0]
            data['geom_raw'] = parts[1]
        if i == 1:
            assert len(parts) == 1
            assert len(parts[0].split('/')) == 2
            data['upper_raw'], data['lower_raw'] = [p.strip() for p in parts[0].split('/')]
        if i == 2:
            if parts:
                data['notes'] = '\n'.join(parts)
    return data


def parse_55_tr(tr):
    tds = tr.find_all('td')
    if len(tds) != 4:
        return

    data = dict()
    for i, td in enumerate(tds):
        parts = [l.strip() for l in td.text.splitlines() if l.strip()]
        if i == 0:
            assert len(parts) == 2
            data['name'] = parts[0]
            data['geom_raw'] = parts[1]
        if i == 1:
            if len(parts) == 3:
                data['upper_raw'] = parts[0]
                data['lower_raw'] = parts[2]
            else:
                assert len(parts) == 2
                data['upper_raw'] = parts[0].split(' /')[0]
                data['lower_raw'] = parts[1]
        if i == 3:
            data['notes'] = '\n'.join(parts)
    return data


def parse_airport(soup, airport):
    airspaces = list()

    h4s = soup.find_all('h4')
    h4 = [h4 for h4 in h4s if '2.17' in h4.span.text][0]
    table = h4.find_next_sibling('table')
    trs = table.find_all('tr')

    for tr in trs:
        tds = tr.find_all('td')
        if tds[1].text.strip() == 'Vertical limits':
            text = tds[2].text.strip()
            limit_lines = [l.strip() for l in text.splitlines() if l.strip()]

            if airport == 'LHSM':
                text = tds[3].text.strip()
                limit_lines += [l.strip() for l in text.splitlines() if l.strip()]

        if tds[1].text.strip() == 'Designation and lateral limits':
            text = tds[2].text.strip()
            geom_lines = [l.strip() for l in text.splitlines() if l.strip()]

            if airport == 'LHSM':
                text = tds[3].text.strip()
                geom_lines += [l.strip() for l in text.splitlines() if l.strip()]

            if airport == 'LHUD':
                geom = list()
                next_trs = tr.find_next_siblings('tr')
                for ntr in next_trs:
                    ntds = ntr.find_all('td')
                    text = ntds[0].text.strip()
                    if text == '2':
                        break
                    geom.append(' '.join([ntd.text.strip() for ntd in ntds[-2:]]))
                geom_lines.append(', '.join(geom))


    assert limit_lines and geom_lines

    if airport == 'LHBC':
        data = {
            'name': ' '.join(geom_lines[:2]),
            'geom_raw': geom_lines[2],
            'upper_raw': limit_lines[0].rstrip(' /'),
            'lower_raw': limit_lines[1],
            'notes': airport
        }
        data['class'] = get_class_from_name(data['name'])
        airspaces.append(data)

    elif airport == 'LHBP' or airport == 'LHUD':
        upper, lower = limit_lines[0].split('/ ')
        data = {
            'name': geom_lines[0],
            'geom_raw': geom_lines[1],
            'upper_raw': upper,
            'lower_raw': lower,
            'notes': airport
        }
        data['class'] = get_class_from_name(data['name'])
        airspaces.append(data)

    elif airport == 'LHDC':
        for l in geom_lines:
            name, geom = l.split(u'\ufffd')
            limit = [ll.lstrip(name) for ll in limit_lines if ll.startswith(name)][0]
            upper, lower = limit.split(' / ')
            data = {
                'name': name,
                'geom_raw': geom,
                'upper_raw': upper,
                'lower_raw': lower,
                'notes': airport
            }
            data['class'] = get_class_from_name(data['name'])
            airspaces.append(data)

    elif airport == 'LHFM':
        lower, upper = limit_lines[0].split(' to ')
        lower = lower.replace('SFC', 'GND')
        data = {
            'name': geom_lines[0],
            'geom_raw': geom_lines[1],
            'upper_raw': upper,
            'lower_raw': lower,
            'notes': airport
        }
        data['class'] = get_class_from_name(data['name'])
        airspaces.append(data)

    elif airport == 'LHNY':
        upper, lower = limit_lines[0].split(' ALT ')
        data = {
            'name': geom_lines[0],
            'geom_raw': geom_lines[1],
            'upper_raw': upper,
            'lower_raw': lower,
            'notes': airport
        }
        data['class'] = get_class_from_name(data['name'])
        airspaces.append(data)

    elif airport == 'LHPP' or airport == 'LHPR':

        data = {
            'name': geom_lines[0],
            'geom_raw': geom_lines[1],
            'upper_raw': limit_lines[0],
            'lower_raw': limit_lines[1],
            'notes': airport
        }
        data['class'] = get_class_from_name(data['name'])
        airspaces.append(data)

    elif airport == 'LHSM':
        # data 1
        upper, lower = limit_lines[1].split(' / ')
        data = {
            'name': geom_lines[0],
            'geom_raw': geom_lines[1],
            'upper_raw': upper,
            'lower_raw': lower,
            'notes': airport
        }
        data['class'] = get_class_from_name(data['name'])
        airspaces.append(data)

        # data 2
        upper, lower = limit_lines[3].split(' / ')
        data = {
            'name': geom_lines[2],
            'geom_raw': geom_lines[3],
            'upper_raw': upper,
            'lower_raw': lower,
            'notes': airport
        }
        data['class'] = get_class_from_name(data['name'])
        airspaces.append(data)

    else:
        pp(geom_lines)
        pp(limit_lines)
        raise ValueError('Unknown airport', airport)

    return airspaces


def get_class_from_name(name):
    classes = ['MCTR', 'CTR', 'MTMA', 'TMA', 'CTA', 'TIZ']
    for c in classes:
        if c in name:
            return c
    else:
        raise ValueError('No class found', name)



version = '2015-04-30'

html_dir = os.path.join('data', 'aip', 'html')
json_dir = os.path.join('data', 'aip', 'json')

airports = ['LHBC', 'LHBP', 'LHDC', 'LHFM', 'LHNY', 'LHPP', 'LHPR', 'LHSM', 'LHUD']

chapters = {
    '2.1': parse_2,
    '2.2': parse_2,
    '5.1': parse_5,
    '5.2': parse_5,
    '5.5': parse_5,
    '5.6': parse_5,
}
