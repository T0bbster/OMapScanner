import aiohttp
import asyncio
from util.log import log
from pathlib import Path
from progress.bar import ChargingBar
import urllib
from urllib.parse import urlsplit, urljoin
from urllib.error import HTTPError


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


def try_download_images(base_url, img_dir, save_dir, imgs, exts):
    failed_imgs = []
    bar = ChargingBar('Downloading ', max=len(imgs), suffix='%(index)d/%(max)d - %(eta)ds remaining')
    for img in imgs:
        success = try_download_image(base_url, img_dir, save_dir, img, exts)
        if not success:
            failed_imgs.append(img)
        else:
            bar.next()
    bar.finish()
    return failed_imgs

################################################################

chunk_size = 256 * 1024
async def download_async(session, url, filename):
    async with session.get(url) as response:
        if response.status == 200:
            with open(filename, 'wb') as fd:
                while True:
                    chunk = await response.content.read(chunk_size)
                    if not chunk:
                        break
                    fd.write(chunk)
        else:
            raise HTTPError(url, response.status, '', None, None)


async def try_download_image_async(session, base_url, img_dir, save_dir, img, exts):
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
            await download_async(session, img_url, file)
            log.info(f'Saved {file.as_posix()}')
            res = True
        except HTTPError as e:
            log.add().debug(f'{str(e)}: {file.as_posix()}').sub()
    log.sub()
    return res, img


async def try_download_images_async(session, base_url, img_dir, save_dir, imgs, exts):
    failed_imgs = []
    bar = ChargingBar('Downloading ', max=len(imgs), suffix='%(index)d/%(max)d - %(eta)ds remaining')

    fetch = lambda img: try_download_image_async(session, base_url, img_dir, save_dir, img, exts)
    for answer in asyncio.as_completed([fetch(img) for img in imgs]):
        success, img = await answer
        if not success:
            failed_imgs.append(img)
        else:
            bar.next()
    bar.finish()
    return failed_imgs


async def download_images_async(base_url, img_dir, save_dir, imgs, exts):
    async with aiohttp.ClientSession() as session:
        await try_download_images_async(session, base_url, img_dir, save_dir, imgs, exts)