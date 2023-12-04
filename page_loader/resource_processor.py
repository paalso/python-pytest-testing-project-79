# page_loader/resource_processor.py
import os
import shutil
import requests
from . import url_utils


class ResourceProcessor:
    def __init__(self, download_manager):
        self.__download_manager = download_manager
        self.__full_domain = url_utils.full_domain(self.__download_manager.url)
        self.__base_url = url_utils.base_url(self.__download_manager.url)
        self.__domain = url_utils.domain(self.__download_manager.url)
        self.__resources_dir = url_utils.dirname_for_web_resources(
            url_utils.filename_from_url(self.__download_manager.url))

        self.__resources_path = url_utils.dirname_for_web_resources(
            self.__download_manager.path_to_save_page_content)

        self.__logger = self.__download_manager.logger
        # self.__log_attributes()

    def download_resources(self):
        resources = self.__get_page_resources()

        if not resources:
            return

        self.__make_resources_dir()

        processed_resources_results = [
            self.__process_resource(resource)
            for resource in resources
        ]
        processed_resources_exist = any(processed_resources_results)

        if not processed_resources_exist:
            self.__remove_resources_dir()

    def __get_page_resources(self):
        return [resource for tag in self.__download_manager.resource_tags
                for resource in self.__download_manager.soup.find_all(tag)]

    def __process_resource(self, resource):
        resource_url = self.__get_resource_url(resource)

        if self.__should_ignore_host(resource_url):
            return False

        resource_full_url = self.__get_full_url(resource_url)
        path_to_save = self.__get_path_to_save_resource(resource_full_url)
        self.__download_resource(resource_full_url, path_to_save)
        self.__update_resource_link(resource, resource_full_url)
        return True

    def __should_ignore_host(self, resource_path):
        return self.__download_manager.ignore_other_hosts and \
            self.__is_other_domain(resource_path)

    def __update_resource_link(self, resource, resource_full_url):
        new_resource_link = self.__get_resource_updated_link(resource_full_url)
        resource_link_attr = self.__get_resource_link_attr(resource)
        resource[resource_link_attr] = new_resource_link

    def __get_resource_url(self, resource):
        resource_link_attr = self.__get_resource_link_attr(resource)
        url = resource.get(resource_link_attr)
        self.__logger.debug(f'Resource URL: {url}')
        return url

    # TODO: maybe refactor using page_loader.url_utils.full_url?
    def __get_full_url(self, resource_path):
        if not url_utils.extension(resource_path):
            resource_path = f"{resource_path.rstrip('/')}.html"

        if url_utils.domain(resource_path):
            self.__logger.debug(f'Resource is an absolute URL: {resource_path}')
            return resource_path

        if url_utils.is_absolute_path(resource_path):
            full_url = f'{self.__full_domain}{resource_path}'
            self.__logger.debug(f'Full URL for absolute path: {full_url}')
            return full_url

        full_url = f'{self.__base_url}{resource_path}'
        self.__logger.debug(f'Full URL for relative path: {full_url}')
        return full_url

    def __make_resources_dir(self):
        os.makedirs(self.__resources_path)
        self.__logger.debug(
            f'Created resources directory: {self.__resources_path}')

    def __remove_resources_dir(self):
        shutil.rmtree(self.__resources_path)
        self.__logger.debug(
            f'Removed empty resources directory: {self.__resources_path}')

    # TODO: Maybe refactoring is needed again
    # TODO: Move a resource processing logic to a separate class
    def __get_resource_updated_link(self, resource_full_url):
        base_path_to_save = url_utils.filename_from_full_url(resource_full_url)
        updated_link = os.path.join(self.__resources_dir, base_path_to_save)
        self.__logger.debug(f'Updated resource link: {updated_link}')
        return updated_link

    def __get_path_to_save_resource(self, resource_full_url):
        resource_new_link = self.__get_resource_updated_link(resource_full_url)
        path_to_save = os.path.join(
            self.__download_manager.path, resource_new_link)
        self.__logger.debug(f'Path to save resource: {path_to_save}')
        return path_to_save

    def __get_resource_link_attr(self, resource):
        resource_name = resource.name
        return self.__download_manager.resource_tags[resource_name]

    def __is_other_domain(self, resource_url):
        resource_domain = url_utils.domain(resource_url)
        return resource_domain != '' and resource_domain != self.__domain

    def __download_resource(self, url, save_path):
        response = requests.get(url)
        if response.ok:
            with open(save_path, 'wb') as f:
                f.write(response.content)
            self.__logger.info(
                f"resource file '{url}' downloaded successfully"
                f"and saved to '{save_path}'")
        else:
            self.__logger.error(
                f'Failed to download resource.'
                f'Status code: {response.status_code}')

    def __log_attributes(self):
        self.__logger.debug(f'{self.__class__.__name__} initialized')
        self.__logger.debug(f'__path: {self.__download_manager.path}')
        self.__logger.debug(f'__url: {self.__download_manager.url}')
        self.__logger.debug(f'__base_url: {self.__base_url}')
        self.__logger.debug(f'__domain: {self.__domain}')
        self.__logger.debug(f'__full_domain: {self.__full_domain}')
        self.__logger.debug(f'__resources_dir: {self.__resources_dir}')
        self.__logger.debug(
            f'__page_content_filename: '
            f'{self.__download_manager.page_content_filename}')
        self.__logger.debug(
            f'path_to_save_page_content: '
            f'{self.__download_manager.path_to_save_page_content}')
        self.__logger.debug(f'self.resources_path: {self.__resources_path}')
