import os
import re
import requests
from bs4 import BeautifulSoup
import urllib.parse


class PageLoader:
    def __init__(self, url, path=None):
        self.url = url
        self.path = path or ''
        self.path_to_save_page_content = os.path.join(
            self.path,
            self.__get_filename_for_saving_web_content()
        )
        self.page_content = self.__get_page_content()
        self.soup = BeautifulSoup(self.page_content, 'html.parser')
        print(self.__get_page_image_links())

    def download(self):
        with open(self.path_to_save_page_content, 'w') as f:
            f.write(self.page_content)

        return self.path_to_save_page_content

    def __get_page_content(self):
        request = requests.get(self.url)
        return request.text

    def __get_filename_for_saving_web_content(self):
        if self.url.startswith('http'):
            _, url = self.url.split('//')
        url = url.rstrip('/')

        separators = re.compile(r'[./]')
        url_tokens = separators.split(url)
        base_filename = '-'.join(url_tokens)

        return f'{base_filename}.html'

    def __get_dirname_for_saving_web_resources(self, content_filename):
        basename, _ = content_filename.split('.')
        return f'{basename}_files'

    def __get_page_resources_full_links(self):
        links = self.__get_page_image_links()
        full_links = [self.__get_full_resource_link(link) for link in links]
        return full_links

    def __get_page_image_links(self):
        image_links = (img.get('src') for img in self.soup.find_all('img'))
        image_full_links = [self.__get_full_resource_link(link)
                            for link in image_links]
        return image_full_links

    def __get_full_resource_link(self, partial_link):
        if urllib.parse.urlparse(partial_link).scheme:
            return partial_link
        return urllib.parse.urljoin(self.url, partial_link)


def download(url, path=None):
    page_loader = PageLoader(url, path)
    return page_loader.download()
