# page_loader/download_manager.py
import os
import requests
from bs4 import BeautifulSoup

from . import url_utils
from .resource_processor import ResourceProcessor
from .logger import Logger


class DownloadManager:
    RESOURCE_TAGS = {
        'img': 'src',
        'link': 'href',
        'script': 'src',
        'video': 'src',
        'audio': 'src',
        'source': 'srcset'
    }

    def __init__(self, url, path):
        self.__url = url
        self.__soup = BeautifulSoup(
            self.__get_raw_page_content(), 'html.parser')

        self.page_content_filename = url_utils.filename_from_url(self.__url)
        self.path_to_save_page_content = os.path.join(
            path, self.page_content_filename)

        self.__ignore_other_hosts = True
        self.__prettify = True

        self.__resource_processor = ResourceProcessor(
            url,
            self.__class__.RESOURCE_TAGS,
            self.__soup,
            path,
            self.__ignore_other_hosts
        )

        self.__logger = Logger(self.page_content_filename)

    def download(self):
        self.__logger.info(f"Start download from '{self.__url}'")

        self.__resource_processor.download_resources()
        self.__download_page()
        return self.path_to_save_page_content

    def __download_page(self):
        if self.__prettify:
            processed_page_content = self.__soup.prettify()
        else:
            processed_page_content = str(self.__soup)

        with open(self.path_to_save_page_content, 'w') as f:
            f.write(processed_page_content)

        self.__logger.info(
            f"page content from '{self.__url}' downloaded successfully"
            f"and saved to '{self.path_to_save_page_content}'")

    def __get_raw_page_content(self):
        request = requests.get(self.__url)
        return request.text
