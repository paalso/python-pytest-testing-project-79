import os
import requests_mock
import tempfile
import pytest
import shutil
from bs4 import BeautifulSoup

from page_loader.page_loader import download

URL = 'https://ru.hexlet.io/courses'


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

        # Mock the image resources
        inner_image1_url = 'https://ru.hexlet.io/assets/professions/python.png'
        inner_image1_content = b'Some image content'
        m.get(inner_image1_url, content=inner_image1_content)

        inner_image2_url = 'https://ru.hexlet.io/assets/professions/python.jpg'  # Updated URL
        inner_image2_content = b'Some updated image content'  # You can update the content if needed
        m.get(inner_image2_url, content=inner_image2_content)  # Updated mock for the modified image

        external_image_url = 'https://external.net/images/external-image.png'
        external_image_content = b'Some external image content'
        m.get(external_image_url, content=external_image_content)

        # Mock the script resource
        script_url = 'https://ru.hexlet.io/packs/js/runtime.js'
        script_content = b'Some script content'
        m.get(script_url, content=script_content)

        # Mock the stylesheet resource
        stylesheet_url = 'https://ru.hexlet.io/assets/application.css'
        stylesheet_content = b'Some stylesheet content'
        m.get(stylesheet_url, content=stylesheet_content)

        return m


@pytest.fixture
def temp_directory():
    with tempfile.TemporaryDirectory() as temp_dir:
        subdir = os.path.join('some_dir', 'subdir')
        subdir_path = os.path.join(temp_dir, subdir)
        os.makedirs(subdir_path)
        return temp_dir, subdir_path


def test_download_return_value_with_none_path(
        retrieved_content, cleanup_downloaded_files, setup_mocking):
    with setup_mocking:
        result_path = download(URL)
        assert os.path.isfile(result_path)
        assert result_path == 'ru-hexlet-io-courses.html'


def test_download_html(
        expected_content, retrieved_content, setup_mocking, temp_directory):
    temp_dir, subdir_path = temp_directory
    with setup_mocking:
        result_path = download(URL, path=subdir_path)

        assert os.path.isfile(result_path)
        expected_saved_html_path = os.path.join(
            subdir_path, 'ru-hexlet-io-courses.html'
        )
        assert result_path == expected_saved_html_path
        with open(result_path, 'r') as f:
            assert compare_prettified_htmls(f.read(), expected_content)


def test_download_images(
        expected_content, retrieved_content, setup_mocking, temp_directory):

    temp_dir, subdir_path = temp_directory
    with (setup_mocking):
        download(URL, path=subdir_path)
        expected_saved_resources_dir_path = os.path.join(
            subdir_path, 'ru-hexlet-io-courses_files'
        )
        expected_saved_html_path = os.path.join(
            subdir_path, 'ru-hexlet-io-courses.html'
        )
        with open(expected_saved_html_path, 'r') as file:
            expected_saved_html_content = file.read()

        assert os.path.isdir(expected_saved_resources_dir_path)

        # Check img links like src="/assets/professions/python.png" download
        expected_image1_link_in_saved_html = \
            ('ru-hexlet-io-courses_files/'
             'ru-hexlet-io-assets-professions-python.png')
        assert expected_image1_link_in_saved_html in expected_saved_html_content

        expected_saved_image1_path = os.path.join(
            expected_saved_resources_dir_path,
            'ru-hexlet-io-assets-professions-python.png',
        )
        assert os.path.isfile(expected_saved_image1_path)

        # Check that images from external links are not saved
        external_image_files = [
            file for file in os.listdir(expected_saved_resources_dir_path)
            if "external-image.png" in file
        ]
        assert not external_image_files
