# page_loader/download_manager.py
import json
import os
import requests
from bs4 import BeautifulSoup

from . import url_utils
from .resource_processor import ResourceProcessor
from .logger import Logger

SETTINGS = os.path.join('page_loader', 'settings.json')


class DownloadManager:
    def __init__(self, url, path):
        self.url = url
        self.path = path or ''

        self.soup = BeautifulSoup(
            self.__get_raw_page_content(), 'html.parser')

        self.page_content_filename = url_utils.filename_from_url(self.url)
        self.path_to_save_page_content = os.path.join(
            path, self.page_content_filename)
        self.logger = Logger(self.page_content_filename)
        self.__log_attributes()

        self.__resource_processor = ResourceProcessor(self)
        self.__get_settings()

    def download(self):
        self.logger.info(f"Start download from '{self.url}'")

        self.__resource_processor.download_resources()
        self.__download_page()
        return self.path_to_save_page_content

    def __download_page(self):
        processed_page_content = self.__process_page_content()
        self.__save_page_content(processed_page_content)

    def __process_page_content(self):
        return self.soup.prettify() if self.__prettify else str(self.soup)

    def __save_page_content(self, content):
        with open(self.path_to_save_page_content, 'w') as f:
            f.write(content)

        self.logger.info(
            f"page content from '{self.url}' downloaded successfully "
            f"and saved to '{self.path_to_save_page_content}'")

    def __get_raw_page_content(self):
        request = requests.get(self.url)
        return request.text

    def __get_settings(self):
        with open(SETTINGS, 'r') as settings_file:
            self.__settings = json.load(settings_file)

        self.resource_tags = self.__settings['resource_tags']
        self.ignore_other_hosts = self.__settings['ignore_other_hosts']
        self.__prettify = self.__settings['prettify']

    def __log_attributes(self):
        self.logger.debug(f'{self.__class__.__name__} initialized')
        self.logger.debug(f'Log level: {self.logger.log_level}')
        self.logger.debug(f'Log path: {self.logger.log_path}')
        self.logger.debug(f'page_content_filename:'
                          f'{self.page_content_filename}')
        self.logger.debug(f'path_to_save_page_content:'
                          f'{self.path_to_save_page_content}')
