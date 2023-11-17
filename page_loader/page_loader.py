import os
import requests
from bs4 import BeautifulSoup
from . import url_utils


class PageLoader:
    RESOURCE_TAGS = {
        'img': 'src',
        'link': 'href',
        'video': 'src',
        'audio': 'src'
    }

    def __init__(self, url, path=None):
        path = path or ''
        self.url = url
        netloc = url_utils.netloc(url)
        self.netloc_prefix = netloc.replace('.', '-')
        self.path_to_save_page_content = os.path.join(
            path, url_utils.filename_from_url(self.url))
        self.resources_dir = url_utils.dirname_for_web_resources(
            url_utils.filename_from_url(self.url))
        self.resources_path = url_utils.dirname_for_web_resources(
            self.path_to_save_page_content)
        original_page_content = self.__get_raw_page_content()
        self.soup = BeautifulSoup(original_page_content, 'html.parser')

    def download(self):
        self.__download_resources()
        self.__download_page()
        return self.path_to_save_page_content

    def __download_page(self):
        processed_page_content = self.soup.prettify()
        with open(self.path_to_save_page_content, 'w') as f:
            f.write(processed_page_content)

    def __download_resources(self):
        if self.__get_page_resources():
            os.makedirs(self.resources_path)

        for resource in self.__get_page_resources():
            resource_path = self.__get_resource_path(resource)
            resource_full_url = url_utils.full_url(self.url, resource_path)
            path_to_save = self.__get_path_to_save_recourse(resource_path)
            self.__download_resource(resource_full_url, path_to_save)

            new_resource_basename = os.path.basename(path_to_save)
            new_resource_path = os.path.join(
                self.resources_dir, new_resource_basename)
            resource_link_attr = self.__get_resource_link_attr(resource)
            resource[resource_link_attr] = new_resource_path

    def __get_resource_link_attr(self, resource):
        resource_name = resource.name
        return self.__class__.RESOURCE_TAGS[resource_name]

    def __get_resource_path(self, resource):
        resource_link_attr = self.__get_resource_link_attr(resource)
        return resource.get(resource_link_attr)

    def __get_raw_page_content(self):
        request = requests.get(self.url)
        return request.text

    def __get_page_resources(self):
        return [resource for tag in self.__class__.RESOURCE_TAGS
                for resource in self.soup.find_all(tag)]

    def __get_path_to_save_recourse(self, resource_url):
        return os.path.join(
            self.resources_path,
            f'{self.netloc_prefix}-{url_utils.filename_from_url(resource_url)}')

    @staticmethod
    def __download_resource(url, save_path):
        response = requests.get(url)
        if response.ok:
            with open(save_path, 'wb') as f:
                f.write(response.content)
            print(f"resource file '{url}' downloaded successfully"
                  f"and saved to '{save_path}'")
        else:
            print(f"Failed to download resource."
                  f"Status code: {response.status_code}")


def download(url, path=None):
    page_loader = PageLoader(url, path)
    return page_loader.download()
