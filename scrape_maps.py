import asyncio
from util.log import log
import logging
from pathlib import Path
import numpy as np
from util.timing import time_it
from scraper.scrape_html import get_html
from util.util import parse_img_numbers
from scraper.scrape_images import download_images_async_opt


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
    imgs_to_download, imgs_to_exclude  = find_imgs_to_downloads(save_dir, imgs, exts)

    if imgs_to_exclude:
        print(f'Ignoring {len(imgs_to_exclude)} images')

    n_imgs_to_download = len(imgs_to_download)
    if not imgs_to_download:
        print('Nothing to download')
        return
    else:
        print(f'Trying to download {n_imgs_to_download} images')
    
    loop = asyncio.get_event_loop()
    failed_imgs = loop.run_until_complete(download_images_async_opt(base_url, img_dir, save_dir, imgs, exts))

    n_failed_imgs = len(failed_imgs)
    if failed_imgs:
        print(f'Failed to download {n_failed_imgs}')
        log.warning(f'Failed images: {",".join(failed_imgs)}')
    
    n_downloaded = n_imgs_to_download - n_failed_imgs
    if n_downloaded:
        print(f'Successfully downloaded {n_downloaded} images')


def scrape_from_page(base_url, save_dir, tmp_dir, limit=None):
    img_dir = 'map_images'
    print(f'Downloading from {base_url}')
    print('')

    html = get_html(base_url, tmp_dir)
    img_numbers = parse_img_numbers(html)
    n_imgs = len(img_numbers)
    print(f'Page has a total of {n_imgs} maps')

    img_arr = np.array(img_numbers)
    indices = np.random.randint(n_imgs, size=limit)
    print(f'Downloading a selection of {len(indices)} images')

    if limit and limit >= len(img_numbers):
        limit = None
    download_images(base_url, img_dir, save_dir, img_arr[indices])


def main():
    log.setLevel(logging.DEBUG)
    save_dir = Path('maps/')
    save_dir.mkdir(parents=True, exist_ok=True)

    tmp_dir = Path('tmp/')
    tmp_dir.mkdir(parents=True, exist_ok=True)
    
    base_url = 'http://karten.guedels.ch/'
    scrape_from_page(base_url, save_dir, tmp_dir, limit=50)


if __name__ == "__main__":
    main()