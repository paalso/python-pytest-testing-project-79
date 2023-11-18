import os
from urllib.parse import urlparse, urljoin


def filename_from_url(url):
    """
    Generate a filename from a (possibly partial) url
    """
    url = url.lstrip('/')
    parsed_url = urlparse(url)
    netloc_part = parsed_url.netloc.replace('.', '-')
    path_part = parsed_url.path.replace('/', '-').rstrip('-')
    ext = '' if extension(url) else '.html'
    return f'{netloc_part}{path_part}{ext}'


def dirname_for_web_resources(content_filename, suffix='files'):
    """
    Generate a directory name for saving web resources based
    on the content filename.
    """
    basename, _ = content_filename.split('.')
    return f'{basename}_{suffix}'


def full_url(prefix, url):
    if scheme(url):
        return url
    return urljoin(prefix, url)


def scheme(url):
    return urlparse(url).scheme


def netloc(url):
    return urlparse(url).netloc


def extension(url):
    path = urlparse(url).path
    _, extension = os.path.splitext(path)
    return extension[1:]
