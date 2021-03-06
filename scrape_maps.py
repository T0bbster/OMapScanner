import requests
import urllib.request
from urllib.parse import urlsplit, urljoin
from urllib.error import HTTPError
import logging
import logging.config
from python_log_indenter import IndentedLoggerAdapter
import re
import os
from time import time
from pathlib import Path
from bs4 import BeautifulSoup
from progress.bar import ChargingBar

logging_dir = Path('logs')
logging_dir.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    filename=logging_dir / 'scrape_maps.log',
    format='%(levelname)7s - %(asctime)s: %(message)s'
)
log = IndentedLoggerAdapter(logging.getLogger(__name__))

find_digits = re.compile('\d+')
find_map = re.compile('map=\d+')

def scrape_html(base_url):
    all_maps_query = 'users.php?lastMaps=all'
    r = requests.get(base_url + all_maps_query)
    return r.text


def write_html(file, html):
    with file.open('w', encoding='utf-8') as html_file:
        html_file.write(html)


def get_img_numbers(html):
    return [re.findall(find_digits, match)[0] for match in re.findall(find_map, html)]


def download_image(img_url, file):
    return urllib.request.urlretrieve(img_url, file)


def try_download_image(base_url, img_dir, save_dir, img, exts):
    log.add()
    res = False
    for i, ext in enumerate(exts):
        img_path = Path(img_dir) / f'{img}{ext}'
        img_url = urljoin(base_url, img_path.as_posix())
        file = save_dir / f'{img}{ext}'
        try:
            if not i:
                log.debug(f'Trying to save {img_url} as {file.as_posix()}')
            else:
                log.add().debug(f'Retrying with {ext}... ').sub()
            download_image(img_url, file)
            log.info(f'Saved {file.as_posix()}')
            res = True
        except HTTPError as e:
            log.add().debug(f'{str(e)}: {file.as_posix()}').sub()
    log.sub()
    return res


def find_imgs_to_downloads(save_dir, imgs, exts):
    imgs_to_exclude = []
    imgs_to_download = []
    for img in imgs:
        file_exists = False
        for ext in exts:
            file = save_dir / f'{img}{ext}'
            file_exists = file_exists or file.exists()
        if file_exists:
            imgs_to_exclude.append(img)
        else:
            imgs_to_download.append(img)
    return imgs_to_download, imgs_to_exclude


def download_images(base_url, img_dir, save_dir, imgs):
    exts = ['.jpg', '.png', '.JPG', '.PNG']

    #imgs_to_download, imgs_to_exclude  = find_imgs_to_downloads(save_dir, imgs, exts)
    imgs_to_download = imgs
    imgs_to_exclude = []

    if imgs_to_exclude:
        print(f'Ignoring {len(imgs_to_exclude)} images')

    n_imgs_to_download = len(imgs_to_download)

    if not imgs_to_download:
        print('Nothing to download')
        return
    else:
        print(f'Trying to download {n_imgs_to_download} images')
        
    failed_imgs = []
    bar = ChargingBar('Downloading ', max=n_imgs_to_download, suffix='%(index)d/%(max)d - %(eta)ds remaining')
    for img in imgs_to_download:
        success = try_download_image(base_url, img_dir, save_dir, img, exts)
        if not success:
            failed_imgs.append(img)
        else:
            bar.next()
    bar.finish()

    n_failed_imgs = len(failed_imgs)
    if failed_imgs:
        print(f'Failed to download {n_failed_imgs}')
        log.warning(f'Failed images: {",".join(failed_imgs)}')
    
    n_downloaded = n_imgs_to_download - n_failed_imgs
    if n_downloaded:
        print(f'Successfully downloaded {n_downloaded} images')


def get_html(base_url, tmp_dir):
    name = urlsplit(base_url).netloc
    file = tmp_dir / f'{name}.html'
    if not file.exists():
        print('\tDownloading image list')
        html = scrape_html(base_url)
        #soup = BeautifulSoup(html, features='lxml')
        #soup.script.decompose()
        write_html(file, html)
        return html
    else:
        with file.open('r', encoding='utf-8') as fp:
            return fp.read()


def time_it(func, msg):
    time_start = time()
    res = func()
    time_end = time()
    print(msg.format(time_end - time_start))
    return res


def scrape_from_page(base_url, save_dir, tmp_dir):
    img_dir = 'map_images'
    print(f'Downloading from {base_url}')
    print('')

    html = time_it(lambda: get_html(base_url, tmp_dir), 'Fetched html in {:2.4f} seconds.')
    img_numbers = time_it(lambda: get_img_numbers(html), 'Parsed in {:2.4f} seconds.')

    download_images(base_url, img_dir, save_dir, img_numbers[60:70])


def main():
    log.setLevel(logging.DEBUG)
    save_dir = Path('maps/')
    save_dir.mkdir(parents=True, exist_ok=True)

    tmp_dir = Path('tmp/')
    tmp_dir.mkdir(parents=True, exist_ok=True)
    
    base_url = 'http://karten.guedels.ch/'
    scrape_from_page(base_url, save_dir, tmp_dir)


def test_new_session((base_url, img_dir, save_dir, imgs):
    base_url = 'http://karten.guedels.ch/'
    save_dir = Path('maps/')
    tmp_dir = Path('tmp/')


if __name__ == "__main__":
    main()