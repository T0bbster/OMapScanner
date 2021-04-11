import argparse
from yolov5.utils.google_utils import attempt_download

def download_weights(file, repo='T0bbster/OMapScanner'):
    attempt_download(file, repo)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--weights', type=str, default='yolov5s.pt', help='initial weights path')
    opt = parser.parse_args()

    download_weights(opt.weights)