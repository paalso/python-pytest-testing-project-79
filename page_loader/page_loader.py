import os
import requests
from bs4 import BeautifulSoup
from . import url_utils


class PageLoader:
    def __init__(self, url, path=None):
        self.url = url
        self.path = path or ''
        self.path_to_save_page_content = os.path.join(
            self.path, url_utils.filename_from_url(self.url))
        self.resources_dir = url_utils.dirname_for_web_resources(
            url_utils.filename_from_url(self.url))
        self.resources_path = url_utils.dirname_for_web_resources(
            self.path_to_save_page_content)

        self.original_page_content = self.__get_raw_page_content()
        self.soup = BeautifulSoup(self.original_page_content, 'html.parser')
        self.processed_page_content = self.soup.prettify()
        print()

    def download(self):
        self.__download_resources()

        processed_page_content = self.soup.prettify()
        with open(self.path_to_save_page_content, 'w') as f:
            f.write(processed_page_content)

        return self.path_to_save_page_content

    def __download_resources(self):
        os.makedirs(self.resources_path)
        for resource in self.__get_page_resources():
            resource_path = resource.get('src')
            resource_full_url = url_utils.full_url(self.url, resource_path)
            path_to_save_resource = self.__get_path_to_save_recourse(resource_path)
            new_resource_basename = os.path.basename(path_to_save_resource)
            new_resource_path = os.path.join(self.resources_dir, new_resource_basename)
            self.__download_resource(resource_full_url, path_to_save_resource)
            resource['src'] = new_resource_path
            print()

    def __get_raw_page_content(self):
        request = requests.get(self.url)
        return request.text

    def __get_page_resources(self):
        return self.soup.find_all('img')

    def __get_path_to_save_recourse(self, resource_url):
        return os.path.join(
            self.resources_path,
            url_utils.filename_from_url(resource_url))

    def __download_resource(self, url, save_path):
        response = requests.get(url)
        if response.status_code == 200:
            with open(save_path, 'wb') as f:
                f.write(response.content)
            print(f"resource file '{url}' downloaded successfully"
                  f"and saved to '{save_path}'")
        else:
            print(f"Failed to download image."
                  f"Status code: {response.status_code}")


def download(url, path=None):
    page_loader = PageLoader(url, path)
    return page_loader.download()
