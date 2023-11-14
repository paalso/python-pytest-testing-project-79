import os
import re
import requests


class PageLoader:
    def __init__(self, url, path=None):
        self.url = url
        self.path = path or ''
        self.path_to_save_web_content = os.path.join(
            self.path,
            self.__get_filename_for_saving_web_content()
        )
        self.page_content = self.__get_page_content()

    def download(self):
        with open(self.path_to_save_web_content, 'w') as f:
            f.write(self.page_content)

        return self.path_to_save_web_content

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


def download(url, path=None):
    page_loader = PageLoader(url, path)
    return page_loader.download()
