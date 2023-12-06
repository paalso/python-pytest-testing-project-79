import json
import os
import requests
import requests_mock
import tempfile
import pytest
import shutil
from bs4 import BeautifulSoup


URL = 'https://ru.hexlet.io/courses'
RESOURCES_DIR = 'ru-hexlet-io-courses_files'
CONTENT_FILE = 'ru-hexlet-io-courses.html'

current_file_directory = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(current_file_directory, 'resources.json')) as f:
    RESOURCES = json.load(f)


def compare_prettified_htmls(html_content1, html_content2):
    soap1 = BeautifulSoup(html_content1, 'html.parser')
    soap2 = BeautifulSoup(html_content2, 'html.parser')
    return soap1.prettify() == soap2.prettify()


@pytest.fixture
def retrieved_content(filename):
    with open(os.path.join(current_file_directory, filename)) as f:
        return f.read()


@pytest.fixture
def expected_content():
    with open(os.path.join(current_file_directory, 'expected.html')) as f:
        return f.read()


@pytest.fixture
def cleanup_downloaded_files():
    yield

    if os.path.isfile(CONTENT_FILE):
        os.remove(CONTENT_FILE)
    if os.path.isdir(RESOURCES_DIR):
        shutil.rmtree(RESOURCES_DIR)


@pytest.fixture
def request_status_code(code=200):
    return code


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
def setup_mocking_404():
    with requests_mock.Mocker() as m:
        m.get(URL, status_code=404)
        return m


@pytest.fixture
def temp_directory():
    temp_dir = tempfile.TemporaryDirectory()
    yield temp_dir


@pytest.fixture
def setup_mocking_request_exception():
    with requests_mock.Mocker() as m:
        m.get(URL, exc=requests.exceptions.RequestException(
            'Failed to retrieve content. Error: Simulated RequestException'))
        return m
