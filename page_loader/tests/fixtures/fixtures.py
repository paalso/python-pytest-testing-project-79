import json
import os
import shutil
import tempfile

import pytest
import requests
import requests_mock
from bs4 import BeautifulSoup

# Constants for URL and local file/directory names used in tests
URL = 'https://ru.hexlet.io/courses'
ASSETS_DIR = 'ru-hexlet-io-courses_files'
CONTENT_FILE = 'ru-hexlet-io-courses.html'
HTTP_ERROR_CODES = 400, 401, 403, 404, 405, 408, 500, 501, 502, 503, 504, 505

# Get the directory where this fixtures file is located
current_file_directory = os.path.dirname(os.path.abspath(__file__))

# Load asset metadata from JSON file once for all tests
with open(os.path.join(current_file_directory, 'asset.json')) as f:
    ASSETS = json.load(f)


def compare_prettified_htmls(html_content1, html_content2):
    """
    Compare two HTML strings after parsing and pretty-formatting.
    Returns True if they are structurally identical.
    """
    soap1 = BeautifulSoup(html_content1, 'html.parser')
    soap2 = BeautifulSoup(html_content2, 'html.parser')
    return soap1.prettify() == soap2.prettify()


@pytest.fixture
def retrieved_content(filename):
    """
    Fixture to read and return the contents of a file given by filename,
    relative to the fixtures directory.
    """
    with open(os.path.join(current_file_directory, filename)) as f:
        return f.read()


@pytest.fixture
def expected_content():
    """
    Fixture to read and return the expected HTML content from
    'expected.html' file.
    """
    with open(os.path.join(current_file_directory, 'expected.html')) as f:
        return f.read()


@pytest.fixture
def cleanup_downloaded_files():
    """
    Fixture that yields control to the test, then cleans up downloaded
    HTML file and assets directory after the test finishes.
    """
    yield

    if os.path.isfile(CONTENT_FILE):
        os.remove(CONTENT_FILE)
    if os.path.isdir(ASSETS_DIR):
        shutil.rmtree(ASSETS_DIR)


@pytest.fixture
def setup_mocking(filename):
    """
    Fixture to setup HTTP request mocking using requests_mock.
    It reads the content of `filename`, then mocks GET requests for
    the main URL and asset URLs to return appropriate content.
    """
    with open(os.path.join(current_file_directory, filename)) as f:
        retrieved_content = f.read()

    with requests_mock.Mocker() as m:
        m.get(URL, text=retrieved_content)
        # Mock an example URL, e.g., href="/courses"
        m.get(ASSETS[-1]['url'], text=retrieved_content)

        for asset_data in ASSETS:
            # For assets ending with .html, use retrieved_content
            if asset_data['url'].endswith('html'):
                asset_data['content'] = retrieved_content
            m.get(asset_data['url'], text=asset_data['content'])

        return m


@pytest.fixture
def temp_directory():
    """
    Fixture to create and provide a temporary directory for tests,
    cleaning it up automatically when test finishes.
    """
    temp_dir = tempfile.TemporaryDirectory()
    yield temp_dir


@pytest.fixture
def setup_mocking_http_fail_response(status_code):
    """
    Fixture to mock HTTP GET request to URL returning a specific failure
    status code.
    """
    with requests_mock.Mocker() as m:
        m.get(URL, status_code=status_code)
        return m


@pytest.fixture
def setup_mocking_request_exception():
    """
    Fixture to mock HTTP GET request to URL raising a RequestException,
    simulating network errors.
    """
    with requests_mock.Mocker() as m:
        m.get(URL, exc=requests.exceptions.RequestException(
            'Some simulated RequestException'))
        return m
