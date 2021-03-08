import aiohttp
import asyncio
from pathlib import Path
from progress.bar import ChargingBar
from urllib.parse import urlsplit, urljoin
from util.log import log


chunk_size = 256 * 1024
async def download_async_opt(session, url, file):
    async with session.get(url) as response:
        if response.status == 200:
            with open(file, 'wb') as fd:
                while True:
                    chunk = await response.content.read(chunk_size)
                    if not chunk:
                        break
                    fd.write(chunk)
        else:
            log.debug(f'HTTPError {response.status}: {file.as_posix()} not found')


async def try_download_image_async_opt(session, base_url, img_dir, save_dir, img, exts):
    log.add()
    res = False
    log.debug(f'Trying to fetch {img}')
    for ext in exts:
        img_path = Path(img_dir) / f'{img}{ext}'
        img_url = urljoin(base_url, img_path.as_posix())
        file = save_dir / f'{img}{ext}'
        await download_async_opt(session, img_url, file)
        log.info(f'Saved {file.as_posix()}')
        res = True
    log.sub()
    return res, img


async def try_download_images_async_opt(session, base_url, img_dir, save_dir, imgs, exts):
    failed_imgs = []
    bar = ChargingBar('Downloading ', max=len(imgs), suffix='%(index)d/%(max)d - %(eta)ds remaining')

    fetch = lambda img: try_download_image_async_opt(session, base_url, img_dir, save_dir, img, exts)
    for answer in asyncio.as_completed([fetch(img) for img in imgs]):
        success, img = await answer
        if not success:
            failed_imgs.append(img)
        else:
            bar.next()
    bar.finish()
    return failed_imgs


async def download_images_async_opt(base_url, img_dir, save_dir, imgs, exts):
    async with aiohttp.ClientSession() as session:
        return await try_download_images_async_opt(session, base_url, img_dir, save_dir, imgs, exts)

