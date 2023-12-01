# page_loader/page_loader.py
import requests
from bs4 import BeautifulSoup
from .resource_processor import ResourceProcessor
from .logger import Logger


class PageLoader:
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

        self.__ignore_other_hosts = True
        self.__prettify = True

        self.__resource_processor = ResourceProcessor(
            url,
            self.__class__.RESOURCE_TAGS,
            path,
            self.__ignore_other_hosts
        )

        self.__logger = Logger(self.__resource_processor.page_content_filename)

    def download(self):
        self.__logger.info(f"Start download from '{self.__url}'")

        self.__download_resources()
        self.__download_page()
        return self.__resource_processor.path_to_save_page_content

    def __download_page(self):
        if self.__prettify:
            processed_page_content = self.__soup.prettify()
        else:
            processed_page_content = str(self.__soup)

        path_to_save_page_content = (
            self.__resource_processor.path_to_save_page_content)

        with open(path_to_save_page_content, 'w') as f:
            f.write(processed_page_content)

        self.__logger.info(
            f"page content from '{self.__url}' downloaded successfully"
            f"and saved to '{path_to_save_page_content}'")

    def __download_resources(self):
        resources = self.__get_page_resources()

        if resources:
            self.__resource_processor.download_resources(resources)

    def __get_raw_page_content(self):
        request = requests.get(self.__url)
        return request.text

    def __get_page_resources(self):
        return [resource for tag in self.__class__.RESOURCE_TAGS
                for resource in self.__soup.find_all(tag)]


def download(url, path=None):
    path = path or ''
    page_loader = PageLoader(url, path)
    return page_loader.download()
