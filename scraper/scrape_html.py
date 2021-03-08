import requests
from urllib.parse import urlsplit
from util.timing import time_it


def scrape_html(base_url):
    all_maps_query = 'users.php?lastMaps=all'
    r = requests.get(base_url + all_maps_query)
    return r.text


def write_html(file, html):
    with file.open('w', encoding='utf-8') as html_file:
        html_file.write(html)


def get_html(base_url, tmp_dir):
    name = urlsplit(base_url).netloc
    file = tmp_dir / f'{name}.html'
    if not file.exists():
        print('\tDownloading image list')
        html = scrape_html(base_url)
        write_html(file, html)
        return html
    else:
        with file.open('r', encoding='utf-8') as fp:
            return fp.read()