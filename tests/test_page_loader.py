import os
import requests_mock
import tempfile

from page_loader.page_loader import download


def test_download():
    url = 'https://ru.hexlet.io/courses'
    expected_content = 'Test content'
    subdir = 'some_dir/subdir'

    with tempfile.TemporaryDirectory() as temp_dir:
        subdir_path = os.path.join(temp_dir, subdir)
        os.makedirs(subdir_path)

        with requests_mock.Mocker() as m:
            m.get(url, text=expected_content)

            result_path = download(url, path=subdir_path)

            assert os.path.isfile(result_path)
            with open(result_path, 'r') as f:
                assert f.read() == expected_content
            expected_path = os.path.join(
                subdir_path, 'ru-hexlet-io-courses.html')
            assert os.path.exists(expected_path)
            assert result_path == expected_path


def test_download_return_value_with_none_path():
    url = 'https://ru.hexlet.io/courses'

    with requests_mock.Mocker() as m:
        m.get(url, text='Test content')

        result_path = download(url)
        expected_path = 'ru-hexlet-io-courses.html'
        assert os.path.isfile(expected_path)
        assert result_path == expected_path

        os.remove(expected_path)
