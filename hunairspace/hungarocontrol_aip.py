import os
import requests
from .utils import beautify_html, write_file_contents

url_template = 'http://ais.hungarocontrol.hu/aip/{version}/{version}-AIRAC/html/eAIP/LH-ENR-{chapter}-en-HU.html'


def download_chapter(chapter, version, dir):
    url = url_template.format(version=version, chapter=chapter)
    html_file = os.path.join(dir, '{}.html'.format(chapter))
    if os.path.isfile(html_file):
        return
    print html_file
    r = requests.get(url)
    if r.ok:
        html = beautify_html(r.text)
        write_file_contents(html_file, html)


