# tests/test_page_loader.py
import json
import os
import requests_mock
import tempfile
import pytest
import shutil
from bs4 import BeautifulSoup
import logging

from page_loader import download

URL = 'https://ru.hexlet.io/courses'
RESOURCES_DIR = 'ru-hexlet-io-courses_files'
CONTENT_FILE = 'ru-hexlet-io-courses.html'
with open(os.path.join('tests', 'fixtures', 'resources.json')) as f:
    RESOURCES = json.load(f)


def compare_prettified_htmls(html_content1, html_content2):
    soap1 = BeautifulSoup(html_content1, 'html.parser')
    soap2 = BeautifulSoup(html_content2, 'html.parser')
    return soap1.prettify() == soap2.prettify()


@pytest.fixture
def retrieved_content(filename):
    path = os.path.join('tests', 'fixtures', filename)
    with open(path) as f:
        return f.read()


@pytest.fixture
def expected_content():
    path = os.path.join('tests', 'fixtures', 'expected.html')
    with open(path) as f:
        return f.read()


@pytest.fixture
def cleanup_downloaded_files():
    yield

    if os.path.isfile(CONTENT_FILE):
        os.remove(CONTENT_FILE)
    if os.path.isdir(RESOURCES_DIR):
        shutil.rmtree(RESOURCES_DIR)


@pytest.fixture
def setup_mocking(retrieved_content):
    with requests_mock.Mocker() as m:
        m.get(URL, text=retrieved_content)
        m.get(RESOURCES[-1]['url'], text=retrieved_content)  # href="/courses"
        for resource_data in RESOURCES:
            if resource_data['url'].endswith('html'):
                resource_data['content'] = retrieved_content
            m.get(resource_data['url'], text=resource_data['content'])
        return m


@pytest.fixture
def temp_directory():
    temp_dir = tempfile.TemporaryDirectory()
    yield temp_dir


# Test the download of HTML content
@pytest.mark.parametrize(
    'filename', ['retrieved.html'])
def test_download_html(
        expected_content, retrieved_content, setup_mocking, temp_directory):
    with setup_mocking, temp_directory as temp_dir:
        pass
        result_path = download(URL, path=temp_dir)

        assert os.path.isfile(result_path), "Downloaded HTML file should exist"

        html_path = os.path.join(
            temp_dir, CONTENT_FILE
        )
        assert result_path == html_path, \
            "Downloaded HTML file path should match the expected path"
        with open(result_path, 'r') as f:
            assert compare_prettified_htmls(f.read(), expected_content), \
                "Downloaded HTML content should match the expected content"


# Test the download of resources and ensure proper link transformation
@pytest.mark.parametrize('filename', ['retrieved.html'])
def test_download_resources(
        expected_content, retrieved_content, setup_mocking, temp_directory):
    with setup_mocking, temp_directory as temp_dir:
        download(URL, path=temp_dir)
        resources_dir_path = os.path.join(temp_dir, RESOURCES_DIR)
        assert os.path.exists(resources_dir_path), \
            "Resources directory should exist"
        assert os.path.isdir(resources_dir_path), \
            "Resources path should be a directory"

        html_path = os.path.join(temp_dir, CONTENT_FILE)
        with open(html_path, 'r') as file:
            html_content = file.read()

        for resource_data in RESOURCES:
            path = resource_data['path']
            link = os.path.join(RESOURCES_DIR, path)
            assert link in html_content, \
                f"Link {link} should be present in HTML content"

            resource_path = os.path.join(resources_dir_path, path)
            assert os.path.isfile(resource_path), \
                f"Resource file {resource_path} should exist"

            content = resource_data['content']

            if resource_data['url'].endswith('html'):
                assert compare_prettified_htmls(
                    open(resource_path).read(), content), \
                    f"HTML content of {resource_path} should match"
            else:
                assert open(resource_path).read() == content, \
                    f"Content of {resource_path} should match"

        # Check that images from external links are not saved
        external_resource_files = [
            file for file in os.listdir(resources_dir_path)
            if "external-" in file
        ]
        assert not external_resource_files, \
            "External image files should not be saved"


@pytest.mark.parametrize('filename', ['retrieved_without_resources.html'])
def test_download_html_without_resources_to_download(
        filename, retrieved_content, setup_mocking, temp_directory):
    with setup_mocking, temp_directory as temp_dir:
        download(URL, path=temp_dir)
        resources_dir_path = os.path.join(temp_dir, RESOURCES_DIR)
        assert not os.path.exists(resources_dir_path), \
            f"The resources directory '{RESOURCES_DIR}' should not exist"


@pytest.mark.parametrize(
    'filename', ['retrieved.html', 'retrieved_without_resources.html'])
def test_download_return_value_with_none_path(
        retrieved_content, cleanup_downloaded_files, setup_mocking):
    with setup_mocking:
        result_path = download(URL)
        assert os.path.isfile(result_path), \
            f"Downloaded file {result_path} should exist"
        assert result_path == 'ru-hexlet-io-courses.html', \
            f'Downloaded file path should be {CONTENT_FILE}'


@pytest.mark.parametrize('filename', ['retrieved.html'])
def test_download_logging(
        retrieved_content, setup_mocking, temp_directory, caplog):
    caplog.set_level(level=logging.INFO)
    with setup_mocking, temp_directory as temp_dir:
        download(URL, path=temp_dir)
        log_messages = [record.message for record in caplog.records]
        with open(os.path.join('tests', 'fixtures', 'log_content.txt')) as f:
            for line in f:
                log_line = line.rstrip().replace('dir_to_save', temp_dir)
                assert log_line in log_messages
