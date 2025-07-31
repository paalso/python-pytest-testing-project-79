import json
import os

import requests
from bs4 import BeautifulSoup

from . import url_utils
from .assets_processor import AssetsProcessor
from .exceptions.io_exceptions import DirectoryError, SaveError
from .exceptions.network_exceptions import HttpError, RequestError
from .logger import Logger

SETTINGS_FILE = 'settings.json'


class DownloadManager:
    def __init__(self, url, path):
        self.url = url
        self.path = path or ''
        self._validate_path()

        self.page_content_filename = url_utils.filename_from_url(self.url)
        self.path_to_save_page_content = \
            os.path.join(self.path, self.page_content_filename)
        self.assets_dir = \
            url_utils.dirname_for_web_assets(self.page_content_filename)

        self.logger = Logger(self.page_content_filename)
        self._log_initial_attributes()

        self.soup = self._fetch_page_content()

        if self.soup:
            self._load_settings()
            self.assets_processor = AssetsProcessor(self)

    def download(self):
        if not self.soup:
            return

        try:
            self.assets_processor.download_assets()
            self._save_processed_page()
            return self.path_to_save_page_content
        except Exception as e:
            self.logger.debug(f'Download failed: {e}')
            raise

    def _validate_path(self):
        if self.path and not os.path.exists(self.path):
            raise DirectoryError(f"Directory '{self.path}' does not exist.")

    def _fetch_page_content(self):
        self.logger.debug(f"Start download from '{self.url}'")
        try:
            response = requests.get(self.url)
            if not response.ok:
                msg = (f'Failed to retrieve content. '
                       f'Status code: {response.status_code}')
                self.logger.debug(msg)
                raise HttpError(msg)
            return BeautifulSoup(response.text, 'html.parser')

        except requests.exceptions.RequestException as e:
            msg = f"Failed to retrieve content. Error: {e}"
            self.logger.debug(msg)
            raise RequestError(msg)

    def _load_settings(self):
        settings_path = os.path.join(os.path.dirname(__file__), SETTINGS_FILE)
        with open(settings_path, 'r', encoding='utf-8') as f:
            settings = json.load(f)

        self.asset_tags = settings.get('asset_tags', [])
        self.ignore_other_hosts = settings.get('ignore_other_hosts', True)
        self._prettify = settings.get('prettify', False)

    def _save_processed_page(self):
        html = self._process_html()

        self._check_write_permissions()

        try:
            with open(self.path_to_save_page_content,
                      'w', encoding='utf-8') as f:
                f.write(html)
            self.logger.debug(
                f"Page content from '{self.url}' downloaded successfully "
                f"and saved to '{self.path_to_save_page_content}'"
            )
        except Exception as e:
            self._handle_save_error(e)
            raise SaveError(
                f'Failed to save page content to '
                f'{self.path_to_save_page_content}. Error: {e}'
            )

    def _check_write_permissions(self):
        directory = os.path.dirname(self.path_to_save_page_content)
        if not os.access(directory, os.W_OK):
            raise SaveError(
                f'No write permission to directory: {directory}')

        if os.path.exists(self.path_to_save_page_content):
            if not os.access(self.path_to_save_page_content, os.W_OK):
                raise SaveError(
                    f'No write permission to file: '
                    f'{self.path_to_save_page_content}')

    def _process_html(self):
        return self.soup.prettify() if self._prettify else str(self.soup)

    def _handle_save_error(self, error):
        self.logger.debug(f'Save failed: {error}')
        if os.path.exists(self.path_to_save_page_content):
            os.remove(self.path_to_save_page_content)
        if hasattr(self, 'assets_processor'):
            self.assets_processor.remove_assets_dir()

    def _log_initial_attributes(self):
        self.logger.debug(f'{self.__class__.__name__} initialized')
        self.logger.debug(f'Log level: {self.logger.log_level}')
        self.logger.debug(f'Log path: {self.logger.log_path}')
        self.logger.debug(
            f'page_content_filename: {self.page_content_filename}')
        self.logger.debug(
            f'path_to_save_page_content: {self.path_to_save_page_content}')
        self.logger.debug(f'assets_dir: {self.assets_dir}')
