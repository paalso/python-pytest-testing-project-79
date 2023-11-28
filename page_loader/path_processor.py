# page_loader/path_processor.py
import os
from datetime import datetime
import logging
from . import url_utils

LOGS_DIR = 'logs'
LOG_FILE_TEMPLATE = 'download_{page_content_filename}_{date_time}.log'
TIME_FORMAT = '%Y%m%d_%H%M%S'
os.environ['DEBUG'] = 'true'


class PathProcessor:
    def __init__(self, url, resource_tags, path=None):
        self.__path = path or ''
        self.__url = url
        self.__resource_tags = resource_tags
        self.__full_domain = url_utils.full_domain(url)
        self.__base_url = url_utils.base_url(url)
        self.__domain = url_utils.domain(url)
        self.__resources_dir = url_utils.dirname_for_web_resources(
            url_utils.filename_from_url(self.__url))
        self.__page_content_filename = url_utils.filename_from_url(self.__url)

        self.path_to_save_page_content = os.path.join(
            path, self.__page_content_filename)
        self.resources_path = url_utils.dirname_for_web_resources(
            self.path_to_save_page_content)

        if os.environ.get('DEBUG', '').lower() == 'true':
            self.__setup_logger()
        self.__log_attributes()

    def get_resource_url(self, resource):
        resource_link_attr = self.get_resource_link_attr(resource)
        url = resource.get(resource_link_attr)
        self.logger.debug(f'Resource URL: {url}')
        return url

    def get_resource_full_url(self, resource_path):
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

    # TODO: test it
    def make_resources_dir(self):
        os.makedirs(self.resources_path)
        self.logger.debug(f'Created resources directory: {self.resources_path}')

    # Refactoring is needed again
    # Move a resource processing logic to a separate class
    def get_resource_updated_link(self, resource_full_url):
        base_path_to_save = url_utils.filename_from_full_url(resource_full_url)
        updated_link = os.path.join(self.__resources_dir, base_path_to_save)
        self.logger.debug(f'Updated resource link: {updated_link}')
        return updated_link

    def get_path_to_save_resource(self, resource_full_url):
        resource_new_link = self.get_resource_updated_link(resource_full_url)
        path_to_save = os.path.join(self.__path, resource_new_link)
        self.logger.debug(f'Path to save resource: {path_to_save}')
        return path_to_save

    def get_resource_link_attr(self, resource):
        resource_name = resource.name
        return self.__resource_tags[resource_name]

    def is_other_domain(self, resource_url):
        resource_domain = url_utils.domain(resource_url)
        return resource_domain != '' and resource_domain != self.__domain

    def __setup_logger(self):
        log_file_path = self.__get_log_file_path()
        logging.basicConfig(filename=log_file_path, level=logging.DEBUG)
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(logging.StreamHandler())

    def __get_log_file_path(self):
        log_file_dir = LOGS_DIR
        page_content_filename = self.__page_content_filename.rstrip('.html')
        date_time = datetime.now().strftime(TIME_FORMAT)
        log_file_name = LOG_FILE_TEMPLATE.format(
            page_content_filename=page_content_filename,
            date_time=date_time)

        return os.path.join(log_file_dir, log_file_name)

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
        self.logger.debug(f'self.resources_path: {self.resources_path}')
