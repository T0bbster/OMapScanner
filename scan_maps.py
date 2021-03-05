import easyocr
import os
import argparse

from IPython.display import Image

import PIL
from PIL import ImageDraw
from pathlib import Path

import argparse

from functools import wraps
from time import time
import logging
import traceback

def initialize_reader(languages):
    return easyocr.Reader(lang_list=languages)

def draw_boxes(image, bounds, color='red', width=2):
    draw = ImageDraw.Draw(image)
    for bound in bounds:
        p0, p1, p2, p3 = bound[0]
        draw.line([*p0, *p1, *p2, *p3, *p0], fill=color, width=width)

def draw_boxes_on_image(reader, in_path, out_dir):
    fp = Path(in_path)
    bounds = reader.readtext(in_path)
    image = PIL.Image.open(in_path)
    draw_boxes(image, bounds)
    image.save(os.path.join(out_dir, fp.stem + '.out' + fp.suffix))

def dir_path(path):
    if os.path.isdir(path):
        return path
    else:
        raise argparse.ArgumentTypeError(f"{path} is not a valid path")

def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Parse orienteering maps for meta data'
    )
    parser.add_argument('-dir', '--directory', type=dir_path, help='Directory containing map files', required=True)
    parser.add_argument('-out', '--output-directory', type=str, help='Directory for output. Will be created if it does not exist', default='out')
    parser.add_argument('-l', '--languages', help='Which languages to detect', default=['de'])
    return parser.parse_args()

def main():
    logging.basicConfig(filename='scan_maps.log', encoding='utf-8', level=logging.ERROR)
    parsed_args = parse_arguments()
    out_dir = parsed_args.output_directory
    print(f'Writing output to directory: \'{out_dir}\'')
    if (not os.path.exists(out_dir)):
        print(f'\tCreating directory: \'{out_dir}\'')
        os.mkdir(out_dir)

    print(f'Initializing reader for the languages {parsed_args.languages}... ', end='')
    reader = initialize_reader(parsed_args.languages)
    print('Done.')
    print('')


    print(f'Scanning files in directory: \'{parsed_args.directory}\'')
    failed_files = []
    for root, dirs, files in os.walk(parsed_args.directory):
        for filename in files:
            try:
                print(f'\tScanning {filename}', end='\r')
                time_start = time()
                draw_boxes_on_image(reader, root + '/' + filename, out_dir)
                time_end = time()
                print(f'\tScanned  {filename} in {time_end - time_start:2.4f} sec')
            except Exception as exc:
                logging.error(f'Scanning {filename} failed: ', exc_info=exc)
                failed_files.append(filename)
    
    print('Failed to scan the following files:')
    for file in failed_files:
        print(f'\t{file}')

if __name__ == "__main__":
    main()
    