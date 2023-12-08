# flake8: noqa: F401, F811

import os
import pytest
import logging
from unittest.mock import patch

from page_loader import download


from fixtures.fixtures import (
    URL,
    ASSETS_DIR,
    CONTENT_FILE,
    ASSETS,
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


# Test the download of assets and ensure proper link transformation
@pytest.mark.parametrize('filename', ['retrieved.html'])
def test_download_assets(
        expected_content, retrieved_content, setup_mocking, temp_directory):
    with setup_mocking, temp_directory as temp_dir:
        download(URL, path=temp_dir)
        assets_dir_path = os.path.join(temp_dir, ASSETS_DIR)
        assert os.path.exists(assets_dir_path), \
            "Assets directory should exist"
        assert os.path.isdir(assets_dir_path), \
            "Assets path should be a directory"

        html_path = os.path.join(temp_dir, CONTENT_FILE)
        with open(html_path, 'r') as file:
            html_content = file.read()

        for asset_data in ASSETS:
            path = asset_data['path']
            link = os.path.join(ASSETS_DIR, path)
            assert link in html_content, \
                f"Link {link} should be present in HTML content"

            asset_path = os.path.join(assets_dir_path, path)
            assert os.path.isfile(asset_path), \
                f"Asset file {asset_path} should exist"

            content = asset_data['content']

            if asset_data['url'].endswith('html'):
                assert compare_prettified_htmls(
                    open(asset_path).read(), content), \
                    f"HTML content of {asset_path} should match"
            else:
                assert open(asset_path).read() == content, \
                    f"Content of {asset_path} should match"

        # Check that images from external links are not saved
        external_asset_files = [
            file for file in os.listdir(assets_dir_path)
            if "external-" in file
        ]
        assert not external_asset_files, \
            "External image files should not be saved"


@pytest.mark.parametrize('filename', ['retrieved_without_assets.html'])
def test_download_html_without_assets_to_download(
        filename, retrieved_content, setup_mocking, temp_directory):
    with setup_mocking, temp_directory as temp_dir:
        download(URL, path=temp_dir)
        assets_dir_path = os.path.join(temp_dir, ASSETS_DIR)
        assert not os.path.exists(assets_dir_path), \
            f"The assets directory '{ASSETS_DIR}' should not exist"


@pytest.mark.parametrize(
    'filename', ['retrieved.html', 'retrieved_without_assets.html'])
def test_download_return_value_with_none_path(
        retrieved_content, cleanup_downloaded_files, setup_mocking):
    with setup_mocking:
        result_path = download(URL)
        assert os.path.isfile(result_path), \
            f"Downloaded file {result_path} should exist"
        assert result_path == 'ru-hexlet-io-courses.html', \
            f'Downloaded file path should be {CONTENT_FILE}'
