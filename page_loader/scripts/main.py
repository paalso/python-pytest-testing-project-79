import argparse
import logging
import os
import sys
import time

from page_loader.__version__ import __version__
from page_loader.download_manager import DownloadManager
from page_loader.exceptions.io_exceptions import DirectoryError, SaveError
from page_loader.exceptions.network_exceptions import HttpError, RequestError


def parse_args():
    parser = argparse.ArgumentParser(description='Web page downloader')
    parser.add_argument('url', metavar='url')
    parser.add_argument(
        '-o', '--output',
        help='Output directory',
        default=os.getcwd()
    )
    parser.add_argument(
        '-v', '--version',
        action='version',
        version=f'Page downloader {__version__}',
        help='Show the program version and exit.'
    )
    return parser.parse_args()


def setup_logging():
    log_format = '%(levelname)s:root:%(message)s'

    info_logger = logging.getLogger('info_logger')
    info_logger.setLevel(logging.INFO)
    info_handler = logging.StreamHandler(sys.stdout)
    info_handler.setFormatter(logging.Formatter(log_format))
    info_logger.addHandler(info_handler)

    error_logger = logging.getLogger('error_logger')
    error_logger.setLevel(logging.ERROR)
    error_handler = logging.StreamHandler(sys.stderr)
    error_handler.setFormatter(logging.Formatter(log_format))
    error_logger.addHandler(error_handler)


def log_arguments(logger, args):
    logger.info(f'requested url: {args.url}')
    logger.info(f'output path: {args.output}')


def log_download_info(logger, download_manager):
    path_to_save_page_content = download_manager.assets_dir
    assets_dir = download_manager.assets_dir
    logger.info(f'write html file: {path_to_save_page_content}')
    logger.info(f'create directory for assets: {assets_dir}')


def handle_result(result_path, elapsed_time):
    if result_path:
        print(f'Page was downloaded as \'{result_path}\'')
        print(f'Elapsed time: {elapsed_time:.2f} seconds')
        sys.exit(os.EX_OK)


def run_download(info_logger, error_logger, args):  # noqa: C901
    try:
        start_time = time.time()
        manager = DownloadManager(args.url, args.output)
        result_path = manager.download()

        if result_path is None:
            error_logger.error(
                f'Failed to download page: no content at {args.url}')
            sys.exit(os.EX_OSFILE)

        log_download_info(info_logger, manager)
        handle_result(result_path, time.time() - start_time)

    except (HttpError, RequestError, SaveError, DirectoryError) as e:
        error_logger.error(e)
        exit_codes = {
            HttpError: os.EX_PROTOCOL,
            RequestError: os.EX_UNAVAILABLE,
            SaveError: os.EX_OSFILE,
            DirectoryError: os.EX_IOERR,
        }
        sys.exit(exit_codes[type(e)])

    except Exception as e:
        error_logger.error(f'Some unexpected error:\n{e}')
        sys.exit(os.EX_SOFTWARE)


def main():
    args = parse_args()
    setup_logging()
    info_logger = logging.getLogger('info_logger')
    error_logger = logging.getLogger('error_logger')

    log_arguments(info_logger, args)
    run_download(info_logger, error_logger, args)


if __name__ == '__main__':
    main()
