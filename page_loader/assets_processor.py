import os
import shutil

import requests

from . import url_utils


class AssetsProcessor:
    def __init__(self, download_manager):
        self.__download_manager = download_manager
        self.__full_domain = url_utils.full_domain(self.__download_manager.url)
        self.__base_url = url_utils.base_url(self.__download_manager.url)
        self.__domain = url_utils.domain(self.__download_manager.url)
        self.__assets_dir = self.__download_manager.assets_dir

        self.__assets_path = url_utils.dirname_for_web_assets(
            self.__download_manager.path_to_save_page_content)

        self.__logger = self.__download_manager.logger
        self._log_attributes()

    def download_assets(self):
        assets = self._get_page_assets()

        if not assets or not self._make_assets_dir():
            return

        processed_assets_results = [
            self._process_asset(asset)
            for asset in assets
        ]
        processed_assets_exist = any(processed_assets_results)

        if not processed_assets_exist:
            self.__remove_assets_dir()

    def remove_assets_dir(self):
        try:
            shutil.rmtree(self.__assets_path)
            self.__logger.debug(
                f'Removed assets directory: {self.__assets_path}')
        except Exception as e:
            self.__logger.debug(
                f'Failed to remove assets directory: {self.__assets_path}: {e}')

    def _get_page_assets(self):
        return [asset for tag in self.__download_manager.asset_tags
                for asset in self.__download_manager.soup.find_all(tag)]

    def _process_asset(self, asset):
        asset_url = self._get_asset_url(asset)

        if self._should_ignore_host(asset_url):
            return False

        asset_request_url = self._get_request_url(asset_url)
        asset_url_for_link = self.__get_url_for_link(asset_request_url)
        path_to_save = self._get_path_to_save_asset(asset_url_for_link)
        self._download_asset(asset_request_url, path_to_save)
        self._update_asset_link(asset, asset_url_for_link)
        return True

    def _should_ignore_host(self, asset_path):
        return self.__download_manager.ignore_other_hosts and \
            self._is_other_domain(asset_path)

    def _update_asset_link(self, asset, asset_full_url):
        new_asset_link = self._get_asset_updated_link(asset_full_url)
        asset_link_attr = self._get_asset_link_attr(asset)
        asset[asset_link_attr] = new_asset_link

    def _get_asset_url(self, asset):
        asset_link_attr = self._get_asset_link_attr(asset)
        url = asset.get(asset_link_attr)
        self.__logger.debug(f'Asset URL: {url}')
        return url

    def _get_request_url(self, url):
        if url_utils.domain(url):
            self.__logger.debug(f'Asset is an absolute URL: {url}')
            return url

        if url_utils.is_absolute_path(url):
            full_url = f'{self.__full_domain}{url}'
            self.__logger.debug(f'Full URL for absolute path: {full_url}')
            return full_url

        full_url = f'{self.__base_url}{url}'
        return full_url

    def __get_url_for_link(self, url):
        if not url_utils.extension(url):
            url = f"{url.rstrip('/')}.html"
        return url

    def _get_full_url(self, asset_path, asset):
        if not url_utils.extension(asset_path) and \
                self.__class__._is_html_document_link(asset):
            asset_path = f"{asset_path.rstrip('/')}.html"

        if url_utils.domain(asset_path):
            return asset_path

        if url_utils.is_absolute_path(asset_path):
            full_url = f'{self.__full_domain}{asset_path}'
            return full_url

        full_url = f'{self.__base_url}{asset_path}'
        self.__logger.debug(f'Full URL for relative path: {full_url}')
        return full_url

    # TODO: test it
    def _make_assets_dir(self):
        try:
            os.makedirs(self.__assets_path)
            self.__logger.debug(
                f'Created assets directory: {self.__assets_path}')
            return True

        except OSError as e:
            self.__logger.debug(f'Failed to create assets directory: '
                                f'{self.__assets_path}. Error: {e}')
            return False

    # TODO: Maybe refactoring is needed again
    # TODO: Move an asset processing logic to a separate class
    def _get_asset_updated_link(self, asset_full_url):
        base_path_to_save = url_utils.filename_from_full_url(asset_full_url)
        updated_link = os.path.join(
            self.__download_manager.assets_dir, base_path_to_save)
        self.__logger.debug(f'Updated asset link: {updated_link}')
        return updated_link

    def _get_path_to_save_asset(self, asset_full_url):
        asset_new_link = self._get_asset_updated_link(asset_full_url)
        path_to_save = os.path.join(
            self.__download_manager.path, asset_new_link)
        self.__logger.debug(f'Path to save asset: {path_to_save}')
        return path_to_save

    def _get_asset_link_attr(self, asset):
        asset_name = asset.name
        return self.__download_manager.asset_tags[asset_name]

    @staticmethod
    def _is_html_document_link(asset_tag):
        if asset_tag.name != 'link':
            return False
        rel = asset_tag.get('rel')
        if isinstance(rel, list):
            return 'canonical' in (item.lower() for item in rel)
        if isinstance(rel, str):
            return 'canonical' in rel.lower()
        return False

    def _is_other_domain(self, asset_url):
        asset_domain = url_utils.domain(asset_url)
        return asset_domain != '' and asset_domain != self.__domain

    # TODO: test it
    def _download_asset(self, url, save_path):
        try:
            response = requests.get(url)
            if response.ok:
                with open(save_path, 'wb') as f:
                    f.write(response.content)
                self.__logger.debug(
                    f"asset file '{url}' downloaded successfully "
                    f"and saved to '{save_path}'")
            else:
                self.__logger.debug(
                    f"Failed to download asset file '{url}'"
                    f'Status code: {response.status_code}')
        except requests.exceptions.RequestException as e:
            self.__logger.debug(f"Failed to download asset file '{url}'. "
                                f"Error: {e}")

    def _log_attributes(self):
        self.__logger.debug(f'{self.__class__.__name__} initialized')
        self.__logger.debug(f'domain: {self.__domain}')
        self.__logger.debug(f'base_url: {self.__base_url}')
        self.__logger.debug(f'full_domain: {self.__full_domain}')
        self.__logger.debug(f'assets_path: {self.__assets_path}')
