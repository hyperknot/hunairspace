import os
import shutil
import codecs
import json
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


def pp(data):
    print json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True)


def convert_dms_to_float(deg, min, sec, sign=1):
    return sign * deg + min / 60. + sec / 3600.


def rstrip(string, substr):
    if not string.endswith(substr):
        return string
    return string[:-len(substr)]


def lstrip(string, substr):
    if not string.startswith(substr):
        return string
    return string[len(substr):]


def delete_dir(directory):
    if os.path.exists(directory):
        shutil.rmtree(directory)
