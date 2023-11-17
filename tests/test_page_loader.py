import os
import requests_mock
import tempfile
import pytest
import shutil

from page_loader.page_loader import download

URL = 'https://ru.hexlet.io/courses'


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
        image_url = 'https://ru.hexlet.io/assets/professions/python.png'
        image_content = b'Some image content'
        m.get(image_url, content=image_content)
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
            assert f.read() == expected_content


def test_download_resources(
        expected_content, retrieved_content, setup_mocking, temp_directory):
    temp_dir, subdir_path = temp_directory
    with setup_mocking:
        download(URL, path=subdir_path)
        expected_saved_resources_dir_path = os.path.join(
            subdir_path, 'ru-hexlet-io-courses_files'
        )
        assert os.path.isdir(expected_saved_resources_dir_path)

        expected_saved_image_path = os.path.join(
            expected_saved_resources_dir_path,
            'assets-professions-python.png',
            # 'ru-hexlet-io-assets-professions-python.png',
        )
        assert os.path.isfile(expected_saved_image_path)
