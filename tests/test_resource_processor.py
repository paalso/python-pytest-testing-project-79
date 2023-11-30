# tests/test_resource_processor.py
import os.path

import pytest
import requests_mock
from bs4 import BeautifulSoup
from page_loader.resource_processor import ResourceProcessor

resource_tags = {
    'img': 'src',
    'link': 'href',
    'script': 'src',
}

url = 'https://ru.hexlet.io/courses/'

resource_urls = [
    'https://cdn2.hexlet.io/assets/menu.css',
    'https://ru.hexlet.io/assets/application.css',
    'https://ru.hexlet.io/assets/professions/python.png',
    'https://ru.hexlet.io/courses/assets/professions/python.jpg',
    'https://ru.hexlet.io/courses/assets/python.bmp',
    'https://external.net/images/external-image.png'
]


tags = [
    ('<link rel="stylesheet" href="https://cdn2.hexlet.io/assets/menu.css">', 'link'),
    ('<link rel="stylesheet" media="all" href="/assets/application.css">', 'link'),
    ('<img src="/assets/professions/python.png" alt="Иконка 1">', 'img'),
    ('<img src="assets/professions/python.jpg" alt="Иконка 2">', 'img'),
    ('<img src="https://ru.hexlet.io/courses/assets/python.bmp" alt="Иконка Python 3">', 'img'),
    ('<img src="https://external.net/images/external-image.png" alt="Some external picture">', 'img')
]

resources = [BeautifulSoup(tag, 'html.parser').find(tag_type) for (tag, tag_type) in tags]


@pytest.fixture
def setup_mocking():
    with requests_mock.Mocker() as m:
        m.get(url, text='Mocked retrieved content')
        for resource_url in resource_urls:
            m.get(resource_url, text='Mocked content for resource')
        return m


@pytest.fixture
def resource_processor(tmp_path):
    rp = ResourceProcessor('https://ru.hexlet.io/courses/',
                           resource_tags,
                           os.path.join(tmp_path, 'some_path'))
    return rp


# def test_download_resources(tmp_path):
#     rp = ResourceProcessor(url,
#                            resource_tags,
#                            os.path.join(tmp_path, tmp_path))
#
#     rp.download_resources(resources)
#     assert True

def test_download_resources(resource_processor, setup_mocking):
    with (setup_mocking):
        resource_processor.download_resources(resources)
        assert True