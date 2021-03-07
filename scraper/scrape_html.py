
find_digits = re.compile('\d+')
find_map = re.compile('map=\d+')

def scrape_html(base_url):
    all_maps_query = 'users.php?lastMaps=all'
    r = requests.get(base_url + all_maps_query)
    return r.text


def write_html(file, html):
    with file.open('w', encoding='utf-8') as html_file:
        html_file.write(html)


def time_it(func, msg):
    time_start = time.time()
    res = func()
    time_end = time.time()
    print(msg.format(time_end - time_start))
    return res


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


def scrape_from_page(base_url, save_dir, tmp_dir):
    img_dir = 'map_images'
    print(f'Downloading from {base_url}')
    print('')

    html = time_it(lambda: get_html(base_url, tmp_dir), 'Fetched html in {:2.4f} seconds.')
    img_numbers = time_it(lambda: get_img_numbers(html), 'Parsed in {:2.4f} seconds.')

    download_images(base_url, img_dir, save_dir, img_numbers[60:70])