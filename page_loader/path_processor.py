# page_loader/path_processor.py
import os
from . import url_utils


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

        self.path_to_save_page_content = os.path.join(
            path, url_utils.filename_from_url(self.__url))
        self.resources_path = url_utils.dirname_for_web_resources(
            self.path_to_save_page_content)

    def get_resource_url(self, resource):
        resource_link_attr = self.get_resource_link_attr(resource)
        return resource.get(resource_link_attr)

    def get_resource_full_url(self, resource_path):
        if url_utils.domain(resource_path):
            return resource_path

        if url_utils.is_absolute_path(resource_path):
            return f'{self.__full_domain}{resource_path}'

        return f'{self.__base_url}{resource_path}'

    # TODO: test it
    def make_resources_dir(self):
        os.makedirs(self.resources_path)

    # Refactoring is needed again
    # Move a resource processing logic to a separate class
    def get_resource_updated_link(self, resource_full_url):
        base_path_to_save = url_utils.filename_from_full_url(resource_full_url)
        return os.path.join(self.__resources_dir, base_path_to_save)

    def get_path_to_save_resource(self, resource_full_url):
        resource_new_link = self.get_resource_updated_link(resource_full_url)
        return os.path.join(self.__path, resource_new_link)

    def get_resource_link_attr(self, resource):
        resource_name = resource.name
        return self.__resource_tags[resource_name]

    def is_other_domain(self, resource_url):
        resource_domain = url_utils.domain(resource_url)
        return resource_domain != '' and resource_domain != self.__domain
