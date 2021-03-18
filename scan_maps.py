import easyocr
import os
import argparse

from IPython.display import Image

import PIL
from PIL import ImageDraw
from pathlib import Path

import argparse

from util import dir_path

from functools import wraps
from time import time
import logging
import traceback

def initialize_reader(languages):
    return easyocr.Reader(lang_list=languages)
    

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
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)

    print(f'Initializing reader for the languages {parsed_args.languages}... ', end='')
    reader = initialize_reader(parsed_args.languages)
    print('Done.')
    print('')


if __name__ == "__main__":
    main()
    