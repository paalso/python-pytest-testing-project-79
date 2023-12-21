import argparse
from page_loader.download_manager import DownloadManager
import logging
import sys


def parse_args():
    parser = argparse.ArgumentParser(description='Download web page')

    parser.add_argument('url', metavar='url')
    parser.add_argument('-o', '--output', help='set directory of output')

    return parser.parse_args()


def main():
    args = parse_args()
    url, path = args.url, args.output

    download_manager = DownloadManager(url, path)

    logging.basicConfig(
        level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')

    logging.info(f'requested url: {url}')
    logging.info(f'output path: {path}')

    try:
        result_path = download_manager.download()

        path_to_save_page_content = download_manager.assets_dir
        assets_dir = download_manager.assets_dir
        logging.info(f'write html file: {path_to_save_page_content}')
        logging.info(f'create directory for assets: {assets_dir}')

        if result_path:
            print(f'Page was downloaded as \'{result_path}\'')
            sys.exit(0)

    except Exception as e:
        print(f'Some error(s) occurred: {e}')


if __name__ == '__main__':
    main()
