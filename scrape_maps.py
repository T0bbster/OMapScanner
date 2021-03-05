import requests
import urllib.request
from urllib.parse import urlsplit
import logging
import re
import os
from time import time

base_url = 'http://karten.guedels.ch/'
img_dir = 'map_images/'

find_digits = re.compile('\d+')
find_map = re.compile('map=\d+')

def scrape_html(base_url):
    all_maps_query = 'users.php?lastMaps=all'
    r = requests.get(base_url + all_maps_query)
    return r.text

def write_html(base_url, html, tmp_dir):
    name = urlsplit('http://karten.guedels.ch/').netloc
    with open(f'{name}.html', 'w', encoding='utf-8') as html_file:
        html_file.write(html)


def save_page(base_url):
    tmp_dir = 'tmp/'
    if not os.path.exists(tmp_dir):
        os.mkdir(tmp_dir)
    html = scrape_html(base_url)
    write_html(base_url, html, tmp_dir)


def get_img_numbers(html):
    return [re.findall(find_digits, match)[0] for match in re.findall(find_map, html)]


def download_image(img_url, filename):
    return urllib.request.urlretrieve(img_url, filename)


def try_download_image(base_url, img_dir, save_dir, img, exts):
    for i, ext in enumerate(exts):
        img_url = f'{base_url}{img_dir}{img}{ext}'
        filename = f'{save_dir}/{img}{ext}'
        try:
            if i > 0:
                logging.debug(f'\tRetrying with {ext}... ')
            download_image(img_url, filename)
            return True
        except HTTPError as e:
            logging.debug(f'\t{str(e)}: {filename}')
    return False


def find_imgs_to_downloads(save_dir, imgs, exts):
    imgs_to_exclude = []
    imgs_to_download = []
    for img in imgs:
        file_exists = False
        for ext in exts:
            filename = f'{save_dir}/{img}{ext}'
            file_exists = file_exists or os.path.exists(filename)
        if file_exists:
            imgs_to_exclude.append(img)
        else:
            imgs_to_download.append(img)
    return imgs_to_download, imgs_to_exclude


def download_images(base_url, img_dir, save_dir, imgs):
    exts = ['.jpg', '.png', '.JPG', '.PNG']

    imgs_to_download, imgs_to_exclude  = find_imgs_to_downloads(save_dir, imgs, exts)

    if imgs_to_exclude:
        print(f'Ignoring images: {",".join(imgs_to_exclude)}')

    if imgs_to_download:
        print(f'Downloading images: {",".join(imgs_to_download)}')

    failed_imgs = []
    for img in imgs_to_download:
        success = try_download_image(base_url, img_dir, save_dir, img, exts)
        if not success:
            failed_imgs.append(img)
    if failed_imgs:
        print(f'Failed to download: {",".join(failed_imgs)}')


def main():
    logging.basicConfig(filename='scrape_maps.log', encoding='utf-8', level=logging.ERROR)
    
    save_dir = 'maps'
    if not os.path.exists('maps'):
        os.mkdir(save_dir)
    
    time_start = time()
    download_images(base_url, img_dir, save_dir, img_numbers)
    time_end = time()
    print(f'Took {time_end - time_start:2.4f} seconds to download.')



