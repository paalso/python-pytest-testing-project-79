# tests/test_page_loader.py
# flake8: noqa: F401, F811

import os
import pytest
import logging

from page_loader import download


from fixtures.fixtures import (
    URL,
    RESOURCES_DIR,
    CONTENT_FILE,
    RESOURCES,
    compare_prettified_htmls,
    retrieved_content,
    expected_content,
    cleanup_downloaded_files,
    setup_mocking,
    setup_mocking_404,
    setup_mocking_request_exception,
    temp_directory
)


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


def test_download_html_with_404_status_code(
        setup_mocking_404, temp_directory, caplog):
    with (setup_mocking_404, temp_directory as temp_dir):
        expected_error_message = ('Failed to retrieve content. '
                                  'Server returned status code 404')
        result_path = download(URL, path=temp_dir)
        assert result_path is None, 'Downloaded file should be None'
        assert expected_error_message in caplog.text, \
            'Expected error message found in logs'
        assert not any(os.listdir(temp_dir))


def test_handle_request_exception(
        setup_mocking_request_exception, temp_directory, caplog):
    with (setup_mocking_request_exception, temp_directory as temp_dir):
        result_path = download(URL, path=temp_dir)

        assert result_path is None, 'Downloaded file should be None'

        expected_error_message = ('Failed to retrieve content. '
                                  'Error: Simulated RequestException')
        assert expected_error_message in caplog.text, \
            'Expected error message found in logs.'

        assert not any(os.listdir(temp_dir)), "Temp directory should be empty"
