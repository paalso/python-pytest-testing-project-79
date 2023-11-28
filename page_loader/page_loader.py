# page_loader/page_loader.py
import requests
from bs4 import BeautifulSoup
from .path_processor import PathProcessor


class PageLoader:
    RESOURCE_TAGS = {
        'img': 'src',
        'link': 'href',
        'script': 'src',
        'video': 'src',
        'audio': 'src',
        'source': 'srcset'
    }

    def __init__(self, url, path=None):
        self.__url = url
        self.__path_processor = PathProcessor(
            url, self.__class__.RESOURCE_TAGS, path)
        self.__soup = BeautifulSoup(
            self.__get_raw_page_content(), 'html.parser')

        self.__ignore_other_hosts = True
        self.__prettify = True

    def download(self):
        self.__download_resources()
        self.__download_page()
        return self.__path_processor.path_to_save_page_content

    def __download_page(self):
        if self.__prettify:
            processed_page_content = self.__soup.prettify()
        else:
            processed_page_content = str(self.__soup)
        with open(self.__path_processor.path_to_save_page_content, 'w') as f:
            f.write(processed_page_content)

    def __download_resources(self):
        if self.__get_page_resources():
            self.__path_processor.make_resources_dir()

        for resource in self.__get_page_resources():
            self.__process_resource(resource)

    def __process_resource(self, resource):
        resource_path = self.__path_processor.get_resource_url(resource)

        if self.__ignore_other_hosts and \
           self.__path_processor.is_other_domain(resource_path):
            return

        resource_full_url = self.__path_processor.get_resource_full_url(
            resource_path)

        path_to_save = (
            self.__path_processor.get_path_to_save_resource(resource_full_url))
        self.__download_resource(resource_full_url, path_to_save)

        new_resource_link = (
            self.__path_processor.get_resource_updated_link(resource_full_url))

        resource_link_attr = (
            self.__path_processor.get_resource_link_attr(resource))

        resource[resource_link_attr] = new_resource_link

    def __get_raw_page_content(self):
        request = requests.get(self.__url)
        return request.text

    def __get_page_resources(self):
        return [resource for tag in self.__class__.RESOURCE_TAGS
                for resource in self.__soup.find_all(tag)]

    @staticmethod
    def __download_resource(url, save_path):
        response = requests.get(url)
        if response.ok:
            with open(save_path, 'wb') as f:
                f.write(response.content)
            print(f"resource file '{url}' downloaded successfully"
                  f"and saved to '{save_path}'")
        else:
            print(f'Failed to download resource.'
                  f'Status code: {response.status_code}')


def download(url, path=None):
    page_loader = PageLoader(url, path)
    return page_loader.download()
