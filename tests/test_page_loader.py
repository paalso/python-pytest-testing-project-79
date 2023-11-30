# tests/test_page_loader.py
import os
import requests_mock
import tempfile
import pytest
import shutil
from bs4 import BeautifulSoup

from page_loader.page_loader import download

URL = 'https://ru.hexlet.io/courses'

RESOURCE_URLS = {
    'https://ru.hexlet.io/assets/professions/python.png':
        'Mocked content for /assets/professions/python.png',
    'https://ru.hexlet.io/courses/assets/professions/python.jpg':
        'Mocked content for assets/professions/python.jpg',
    'https://ru.hexlet.io/courses/assets/professions/python.bmp':
        'Mocked content for https://ru.hexlet.io/courses/assets/professions/python.bmp',    # noqa: E501
}


def compare_prettified_htmls(html_content1, html_content2):
    soap1 = BeautifulSoup(html_content1, 'html.parser')
    soap2 = BeautifulSoup(html_content2, 'html.parser')
    return soap1.prettify() == soap2.prettify()


@pytest.fixture
def expected_content():
    path = os.path.join('tests', 'fixtures', 'expected.html')
    with open(path) as f:
        return f.read()


@pytest.fixture
def retrieved_content():
    path = os.path.join('tests', 'fixtures', 'retrieved.html')
    with open(path) as f:
        return f.read()


@pytest.fixture
def cleanup_downloaded_files():
    yield

    path = 'ru-hexlet-io-courses.html'
    if os.path.isfile(path):
        os.remove(path)
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
        return subdir_path


# TODO: remove at the end
def test_zero_test():
    assert True


# Test the download of HTML content
def test_download_html(
        expected_content,
        retrieved_content,
        setup_mocking, temp_directory):
    subdir_path = temp_directory
    with (setup_mocking):
        result_path = download(URL, path=subdir_path)

        assert os.path.isfile(result_path), \
            "Downloaded HTML file should exist"

        html_path = os.path.join(
            subdir_path, 'ru-hexlet-io-courses.html'
        )
        assert result_path == html_path, \
            "Downloaded HTML file path should match the expected path"
        with open(result_path, 'r') as f:
            assert compare_prettified_htmls(f.read(), expected_content), \
                "Downloaded HTML content should match the expected content"


# Test the download of resources (images) and ensure proper link transformation
def test_download_images(
        expected_content, retrieved_content, setup_mocking, temp_directory):
    subdir_path = temp_directory
    with (setup_mocking):
        download(URL, path=subdir_path)
        resources_dir_path = os.path.join(
            subdir_path, 'ru-hexlet-io-courses_files'
        )
        assert os.path.exists(resources_dir_path)
        assert os.path.isdir(resources_dir_path)

        html_path = os.path.join(
            subdir_path, 'ru-hexlet-io-courses.html'
        )
        with open(html_path, 'r') as file:
            html_content = file.read()

        image_links_and_paths = [
            ('ru-hexlet-io-courses_files/ru-hexlet-io-assets-professions-python.png',  # noqa: E501
             'ru-hexlet-io-assets-professions-python.png'),
            ('ru-hexlet-io-courses_files/ru-hexlet-io-courses-assets-professions-python.jpg',  # noqa: E501
             'ru-hexlet-io-courses-assets-professions-python.jpg'),
            ('ru-hexlet-io-courses_files/ru-hexlet-io-courses-assets-professions-python.bmp',  # noqa: E501
             'ru-hexlet-io-courses-assets-professions-python.bmp')
        ]

        for link, path in image_links_and_paths:
            assert link in html_content
            assert os.path.isfile(os.path.join(resources_dir_path, path))

        # Check that images from external links are not saved
        external_image_files = [
            file for file in os.listdir(resources_dir_path)
            if "external-image.png" in file
        ]

        assert not external_image_files
