import os
import re


def download(url, path=None):
    path = path or os.getcwd()
    return path


def get_filename_for_saving_web_content(url):
    if url.startswith('http'):
        _, url = url.split('//')

    separators = re.compile(r'[./]')
    url_tokens = separators.split(url)
    base_filename = '-'.join(url_tokens)

    return f'{base_filename}.html'
