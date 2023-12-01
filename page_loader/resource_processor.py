# page_loader/resource_processor.py
import os
import shutil
import requests
from . import url_utils
from .logger import Logger


class ResourceProcessor:
    def __init__(self, url, resource_tags,
                 path=None, ignore_other_hosts=True):
        self.__path = path or ''
        self.__url = url
        self.__resource_tags = resource_tags
        self.__full_domain = url_utils.full_domain(url)
        self.__base_url = url_utils.base_url(url)
        self.__domain = url_utils.domain(url)
        self.__resources_dir = url_utils.dirname_for_web_resources(
            url_utils.filename_from_url(self.__url))
        self.__page_content_filename = url_utils.filename_from_url(self.__url)
        self.__ignore_other_hosts = ignore_other_hosts

        self.path_to_save_page_content = os.path.join(
            path, self.__page_content_filename)

        self.__resources_path = url_utils.dirname_for_web_resources(
            self.path_to_save_page_content)

        self.logger = Logger(self.__page_content_filename)
        self.__log_attributes()

    def download_resources(self, resources):
        self.__make_resources_dir()

        processed_resources_results = [
            self.__process_resource(resource)
            for resource in resources
        ]
        processed_resources_exist = any(processed_resources_results)

        if not processed_resources_exist:
            self.__remove_resources_dir()

    def __process_resource(self, resource):
        resource_path = self.__get_resource_url(resource)

        if self.__ignore_other_hosts and self.__is_other_domain(resource_path):
            return False

        resource_full_url = self.__get_resource_full_url(resource_path)

        path_to_save = self.__get_path_to_save_resource(resource_full_url)
        self.__download_resource(resource_full_url, path_to_save)

        new_resource_link = self.__get_resource_updated_link(resource_full_url)
        resource_link_attr = self.__get_resource_link_attr(resource)
        resource[resource_link_attr] = new_resource_link

        return True

    def __get_resource_url(self, resource):
        resource_link_attr = self.__get_resource_link_attr(resource)
        url = resource.get(resource_link_attr)
        self.logger.debug(f'Resource URL: {url}')
        return url

    # TODO: maybe refactor using page_loader.url_utils.full_url?
    def __get_resource_full_url(self, resource_path):
        if not url_utils.extension(resource_path):
            resource_path = f"{resource_path.rstrip('/')}.html"

        if url_utils.domain(resource_path):
            self.logger.debug(f'Resource is an absolute URL: {resource_path}')
            return resource_path

        if url_utils.is_absolute_path(resource_path):
            full_url = f'{self.__full_domain}{resource_path}'
            self.logger.debug(f'Full URL for absolute path: {full_url}')
            return full_url

        full_url = f'{self.__base_url}{resource_path}'
        self.logger.debug(f'Full URL for relative path: {full_url}')
        return full_url

    def __make_resources_dir(self):
        os.makedirs(self.__resources_path)
        self.logger.debug(
            f'Created resources directory: {self.__resources_path}')

    def __remove_resources_dir(self):
        shutil.rmtree(self.__resources_path)
        self.logger.debug(
            f'Removed empty resources directory: {self.__resources_path}')

    # TODO: Refactoring is needed again
    # Move a resource processing logic to a separate class
    def __get_resource_updated_link(self, resource_full_url):
        base_path_to_save = url_utils.filename_from_full_url(resource_full_url)
        updated_link = os.path.join(self.__resources_dir, base_path_to_save)
        self.logger.debug(f'Updated resource link: {updated_link}')
        return updated_link

    def __get_path_to_save_resource(self, resource_full_url):
        resource_new_link = self.__get_resource_updated_link(resource_full_url)
        path_to_save = os.path.join(self.__path, resource_new_link)
        self.logger.debug(f'Path to save resource: {path_to_save}')
        return path_to_save

    def __get_resource_link_attr(self, resource):
        resource_name = resource.name
        return self.__resource_tags[resource_name]

    def __is_other_domain(self, resource_url):
        resource_domain = url_utils.domain(resource_url)
        return resource_domain != '' and resource_domain != self.__domain

    def __download_resource(self, url, save_path):
        response = requests.get(url)
        if response.ok:
            with open(save_path, 'wb') as f:
                f.write(response.content)
            self.logger.info(
                f"resource file '{url}' downloaded successfully"
                f"and saved to '{save_path}'")
        else:
            self.logger.info(
                f'Failed to download resource.'
                f'Status code: {response.status_code}')

    def __log_attributes(self):
        self.logger.debug(f'{self.__class__.__name__} initialized')
        self.logger.debug(f'__path: {self.__path}')
        self.logger.debug(f'__url: {self.__url}')
        self.logger.debug(f'__base_url: {self.__base_url}')
        self.logger.debug(f'__domain: {self.__domain}')
        self.logger.debug(f'__full_domain: {self.__full_domain}')
        self.logger.debug(f'__resources_dir: {self.__resources_dir}')
        self.logger.debug(
            f'__page_content_filename: {self.__page_content_filename}')
        self.logger.debug(
            f'path_to_save_page_content: {self.path_to_save_page_content}')
        self.logger.debug(f'self.resources_path: {self.__resources_path}')
