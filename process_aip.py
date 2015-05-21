#!/usr/bin/env python

import os
from hunairspace.utils import ensure_dir, read_file_contents, write_json
from hunairspace.hungarocontrol_aip import download_chapter
from bs4 import BeautifulSoup


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
    data['geometry_raw'] = parts[1]
    data['upper_raw'] = parts[2]
    data['lower_raw'] = parts[3]
    if len(parts) == 5:
        data['class'] = parts[4]
    if len(parts) > 5:
        data['geometry_raw_and'] = parts[5]
        assert parts[6] == data['upper_raw']
        assert parts[7] == data['lower_raw']
    if 'MTMA' in data['name']:
        data['class'] = 'MTMA'
    if 'MCTR' in data['name']:
        data['class'] = 'MCTR'

    assert 'class' in data
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
    tds = tr.findChildren('td')
    if len(tds) != 3:
        return

    data = dict()
    for i, td in enumerate(tds):
        parts = [l.strip() for l in td.text.splitlines() if l.strip()]
        if i == 0:
            assert len(parts) == 2
            data['name'] = parts[0]
            data['geometry_raw'] = parts[1]
        if i == 1:
            assert len(parts) == 1
            assert len(parts[0].split('/')) == 2
            data['upper_raw'], data['lower_raw'] = [p.strip() for p in parts[0].split('/')]
        if i == 2:
            if parts:
                data['notes'] = '\n'.join(parts)
    return data


def parse_55_tr(tr):
    tds = tr.findChildren('td')
    if len(tds) != 4:
        return

    data = dict()
    for i, td in enumerate(tds):
        parts = [l.strip() for l in td.text.splitlines() if l.strip()]
        if i == 0:
            assert len(parts) == 2
            data['name'] = parts[0]
            data['geometry_raw'] = parts[1]
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


def process_chapter(chapter):
    download_chapter(chapter, version, html_dir)
    html_file = os.path.join(html_dir, '{}.html'.format(chapter))
    soup = BeautifulSoup(read_file_contents(html_file))
    data = process_lookup[chapter](soup, chapter)
    write_json('{}.json'.format(chapter), data)


process_lookup = {
    '2.1': parse_2,
    '2.2': parse_2,
    '5.1': parse_5,
    '5.2': parse_5,
    '5.5': parse_5,
    '5.6': parse_5,
}


version = '2015-04-30'
html_dir = os.path.join('data', 'aip', version)
ensure_dir(html_dir)

for chapter in process_lookup:
    process_chapter(chapter)

# process_chapter('5.6')


