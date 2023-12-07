import argparse
from page_loader.page_loader import download
import sys


def parse_args():
    parser = argparse.ArgumentParser(description='Download web page')

    parser.add_argument('url', metavar='url')
    parser.add_argument('-o', '--output', help='set directory of output')

    return parser.parse_args()


def main():
    args = parse_args()
    url, path = args.url, args.output

    result_path = download(url, path)
    if result_path:
        sys.exit(0)


if __name__ == '__main__':
    main()
