import os
import codecs
import json
import requests
from bs4 import BeautifulSoup



def read_json(path, silent=True):
    if not os.path.exists(path) and not silent:
        raise

    try:
        with codecs.open(path, encoding='utf-8') as infile:
            return json.loads(infile.read())
    except Exception:
        if not silent:
            raise


def write_json(path, data):
    with codecs.open(path, 'w', encoding='utf-8') as outfile:
        json.dump(data, outfile, indent=2, ensure_ascii=False, sort_keys=True)


def read_file_contents(path, encoding=True):
    if os.path.exists(path):
        if encoding:
            with codecs.open(path, encoding='utf-8') as infile:
                return infile.read().strip()
        else:
            with open(path) as infile:
                return infile.read().strip()


def write_file_contents(path, data, encoding=True):
    if encoding:
        with codecs.open(path, 'w', encoding='utf-8') as outfile:
            outfile.write(data)
    else:
        with open(path, 'w') as outfile:
            outfile.write(data)


def read_file_contents_as_lines(path):
    if os.path.exists(path):
        with codecs.open(path, encoding='utf-8') as infile:
            content = infile.readlines()
            lines = [line.strip() for line in content]
            return lines


def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


def beautify_html(html):
    soup = BeautifulSoup(html)
    return soup.prettify()
