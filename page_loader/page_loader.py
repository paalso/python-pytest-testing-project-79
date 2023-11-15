import os
import re
import requests
from bs4 import BeautifulSoup
import urllib.parse


class PageLoader:
    def __init__(self, url, path=None):
        self.url = url
        self.netloc = self.__get_netloc()
        self.path = path or ''
        self.path_to_save_page_content = os.path.join(
            self.path,
            self.__get_filename_for_saving_web_content()
        )
        self.raw_page_content = self.__get_raw_page_content()
        self.soup = BeautifulSoup(self.raw_page_content, 'html.parser')
        self.prettified_page_content = self.soup.prettify()
        print(self.url)
        print()
        print(PageLoader.__get_filename_from_url(self.url))
        print(PageLoader.__get_filename_from_url('assets/professions/python.png'))
        print(PageLoader.__get_filename_from_url('https://paalso.github.io/simple_web_page.html'))
        print()
        print(self.__get_filename_for_saving_web_content())

    def download(self):
        with open(self.path_to_save_page_content, 'w') as f:
            f.write(self.prettified_page_content)

        return self.path_to_save_page_content

    def __get_raw_page_content(self):
        request = requests.get(self.url)
        return request.text

    def __get_filename_for_saving_web_content(self):
        """
        Generate a filename for saving the web content based on the URL.

        Example:
            'https://paalso.github.io/simple_web_page/' ->
            'paalso-github-io-simple_web_page.html'
        """
        if self.url.startswith('http'):
            _, url = self.url.split('//')
        url = url.rstrip('/')

        separators = re.compile(r'[./]')
        url_tokens = separators.split(url)
        base_filename = '-'.join(url_tokens)

        return f'{base_filename}.html'

    def __get_dirname_for_saving_web_resources(self, content_filename):
        """
        Generate a directory name for saving web resources based on the content filename.

        Example:
            'paalso-github-io-simple_web_page.html' ->
            'paalso-github-io-simple_web_page_files'
        """
        basename, _ = content_filename.split('.')
        return f'{basename}_files'

    @staticmethod
    def __get_filename_from_url(url):
        """
        Generate a filename from a (possibly partial) url

        Example:
            'assets/img/omelette.png' ->
            'assets-img-omelette.png'
        """
        parsed_url = urllib.parse.urlparse(url)
        netloc_part = parsed_url.netloc.replace('.', '-')
        path_part = parsed_url.path.replace('/', '-')
        return f'{netloc_part}{path_part}'

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

    def __get_netloc(self):
        return urllib.parse.urlparse(self.url).netloc


def download(url, path=None):
    page_loader = PageLoader(url, path)
    return page_loader.download()
