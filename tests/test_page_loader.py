import os
import requests_mock
import tempfile
import pytest

from page_loader.page_loader import download


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


def test_download(expected_content, retrieved_content):
    url = 'https://ru.hexlet.io/courses'
    subdir = os.path.join('some_dir', 'subdir')

    with tempfile.TemporaryDirectory() as temp_dir:
        subdir_path = os.path.join(temp_dir, subdir)
        os.makedirs(subdir_path)

        with requests_mock.Mocker() as m:
            m.get(url, text=retrieved_content)

            result_path = download(url, path=subdir_path)

            assert os.path.isfile(result_path)
            with open(result_path, 'r') as f:
                assert f.read() == expected_content

            expected_saved_html_path = os.path.join(
                subdir_path, 'ru-hexlet-io-courses.html')
            assert os.path.isfile(expected_saved_html_path)
            assert result_path == expected_saved_html_path

            expected_saved_resources_dir_path = os.path.join(
                subdir_path, 'ru-hexlet-io-courses_files')
            assert os.path.isdir(expected_saved_resources_dir_path)

            expected_saved_image_path = os.path.join(
                expected_saved_resources_dir_path,
                'ru-hexlet-io-assets-professions-python.png')
            assert os.path.isfile(expected_saved_image_path)


def test_download_return_value_with_none_path():
    url = 'https://ru.hexlet.io/courses'

    with requests_mock.Mocker() as m:
        m.get(url, text='Test content')

        result_path = download(url)
        expected_path = 'ru-hexlet-io-courses.html'
        assert os.path.isfile(expected_path)
        assert result_path == expected_path

        os.remove(expected_path)
