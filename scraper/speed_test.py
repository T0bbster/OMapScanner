
@contextlib.contextmanager
def report_time(test):
    t0 = time.time()
    yield
    print('Time needed for {} called: {:3.2f}s'.format(test, time.time() - t0))


def remove_files(dir):
    r = glob.glob(dir)
    for i in r:
        os.remove(i)


def pre(start, end):
    imgs = []
    with open('imgs.txt', 'r') as imgs_file:
        imgs = [line.strip() for line in imgs_file.readlines()]
    return imgs


def tests():
    imgs = pre(0, 100)
    
    base_url = 'http://karten.guedels.ch/'
    img_dir = 'map_images'
    save_dir = Path('maps/')
    exts = ['.jpg', '.png', '.JPG', '.PNG']

    loop = asyncio.get_event_loop()
    for max_images in [2, 8, 20, 50]:
        print('*' * 80)
        print('')
        remove_files()
        with report_time('classic'):
            try_download_images(base_url, img_dir, save_dir, imgs[0:max_images], exts)
        print('')

        remove_files()
        with report_time('aiohttp'):
            loop.run_until_complete(download_images_async(base_url, img_dir, save_dir, imgs[0:max_images], exts))
        print('')
            
        remove_files()
        with report_time('aiohttp-opt'):
            loop.run_until_complete(download_images_async_opt(base_url, img_dir, save_dir, imgs[0:max_images], exts))
        print('')


if __name__ == "__main__":
    tests()


