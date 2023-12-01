# page_loader/logger.py
from datetime import datetime
import logging
import os

LOGS_DIR = 'logs'
LOG_FILE_TEMPLATE = 'download_{formatted_page_content_filename}_{date_time}.log'
TIME_FORMAT = '%Y%m%d_%H%M%S'
DEBUG_ENV_VARIABLE = 'DEBUG'


class Logger:
    def __init__(self, page_content_filename, log_level=logging.DEBUG):
        self.__page_content_filename = page_content_filename
        self.log_level = log_level

        logging.basicConfig(filename=self._get_log_file_path(),
                            level=log_level)
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(logging.StreamHandler())
        self.logger.debug(f'log_level: {log_level}')

    def debug(self, message):
        self.logger.debug(message)

    def info(self, message):
        self.logger.info(message)

    def is_debug_enabled(self):
        return os.environ.get(DEBUG_ENV_VARIABLE, '').lower() == 'true'

    def _get_log_file_path(self):
        log_file_dir = LOGS_DIR
        formatted_page_content_filename = (
            self.__page_content_filename.rstrip('.html'))
        date_time = datetime.now().strftime(TIME_FORMAT)
        log_file_name = LOG_FILE_TEMPLATE.format(
            formatted_page_content_filename=formatted_page_content_filename,
            date_time=date_time)

        return os.path.join(log_file_dir, log_file_name)
