import os
import re
import requests


def download(url, path=None):
    path = path or os.getcwd()
    path_to_save_web_content = os.path.join(
        path,
        get_filename_for_saving_web_content(url)    
    )

    request = requests.get(url)
    content_to_save = request.text

    with open(path_to_save_web_content, 'w') as f:
        f.write(content_to_save)

    return path_to_save_web_content


def get_filename_for_saving_web_content(url):
    if url.startswith('http'):
        _, url = url.split('//')
    url = url.rstrip('/')
    
    separators = re.compile(r'[./]')
    url_tokens = separators.split(url)
    base_filename = '-'.join(url_tokens)

    return f'{base_filename}.html'
