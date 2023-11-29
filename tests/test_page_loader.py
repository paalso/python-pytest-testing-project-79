# tests/test_page_loader.py
import os
import requests_mock
import tempfile
import pytest
import shutil
from pathlib import Path
from bs4 import BeautifulSoup

from page_loader.page_loader import download

URL = 'https://ru.hexlet.io/courses'

RESOURCE_URLS = {
    'https://ru.hexlet.io/assets/professions/python.png':
        'Mocked content for python.png'
}


def compare_prettified_htmls(html_content1, html_content2):
    soap1 = BeautifulSoup(html_content1, 'html.parser')
    soap2 = BeautifulSoup(html_content2, 'html.parser')
    return soap1.prettify() == soap2.prettify()


@pytest.fixture
def expected_content():
    path = Path('tests', 'fixtures', 'expected.html')
    with open(path) as f:
        return f.read()


@pytest.fixture
def retrieved_content():
    path = Path('tests', 'fixtures', 'retrieved.html')
    with open(path) as f:
        return f.read()


@pytest.fixture
def cleanup_downloaded_files():
    yield

    expected_path = 'ru-hexlet-io-courses.html'
    if os.path.isfile(expected_path):
        os.remove(expected_path)
    resources_dir = 'ru-hexlet-io-courses_files'
    if os.path.isdir(resources_dir):
        shutil.rmtree(resources_dir)


@pytest.fixture
def setup_mocking(retrieved_content):
    with requests_mock.Mocker() as m:
        m.get(URL, text=retrieved_content)
        for resource_url, resource_text in RESOURCE_URLS.items():
            m.get(resource_url, text='Mocked content for resource')
        return m


@pytest.fixture
def temp_directory():
    with tempfile.TemporaryDirectory() as temp_dir:
        subdir = os.path.join('some_dir', 'subdir')
        subdir_path = os.path.join(temp_dir, subdir)
        os.makedirs(subdir_path)
        return temp_dir, subdir_path


# TODO: remove at the end
def test_zero_test():
    assert True


def test_download_html(
        expected_content,
        retrieved_content,
        setup_mocking, temp_directory):
    temp_dir, subdir_path = temp_directory
    with (setup_mocking):
        result_path = download(URL, path=subdir_path)

        assert os.path.isfile(result_path), \
            "Downloaded HTML file should exist"

        expected_saved_html_path = os.path.join(
            subdir_path, 'ru-hexlet-io-courses.html'
        )
        assert result_path == expected_saved_html_path, \
            "Downloaded HTML file path should match the expected path"
        with open(result_path, 'r') as f:
            assert compare_prettified_htmls(f.read(), expected_content), \
                "Downloaded HTML content should match the expected content"
