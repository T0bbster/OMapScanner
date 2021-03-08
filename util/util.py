import glob
import re
import os


find_digits = re.compile(r'\d+')
find_map = re.compile(r'map=\d+')

def parse_img_numbers(html):
    return [re.findall(find_digits, match)[0] for match in re.findall(find_map, html)]


def remove_files(dir):
    r = glob.glob(dir)
    for i in r:
        os.remove(i)