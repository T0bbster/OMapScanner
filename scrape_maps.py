import asyncio
import argparse
from util.log import log
import logging
from pathlib import Path
import numpy as np
from util.timing import time_it
from scraper.scrape_html import get_html
from util.util import parse_img_numbers
from scraper.scrape_images import download_images_async_opt
from util.util import dir_path


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

    if not limit:
        limit = n_imgs
    else:
        limit = min(limit, n_imgs)

    img_arr = np.array(img_numbers)
    indices = np.random.choice(n_imgs, limit, replace=False)
    print(f'Downloading a selection of {len(indices)} images')

    download_images(base_url, img_dir, save_dir, img_arr[indices])


def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Scrape orienteering maps from a DOMA page'
    )
    parser.add_argument('--url', type=str, help='URL to a doma page', required=True)
    parser.add_argument('--save-dir', type=dir_path, help='Directory to save image files', default='maps')
    parser.add_argument('--tmp-dir', help='Temporary directory', default='tmp')
    parser.add_argument('--limit', type=int, help='Limit images to fetch', default=50)
    return parser.parse_args()


def main(args):
    log.setLevel(logging.DEBUG)

    save_dir = Path(args.save_dir)
    save_dir.mkdir(parents=True, exist_ok=True)

    tmp_dir = Path(args.tmp_dir)
    tmp_dir.mkdir(parents=True, exist_ok=True)
    
    scrape_from_page(args.url, save_dir, tmp_dir, limit=50)


if __name__ == "__main__":
    args = parse_arguments()
    main(args)