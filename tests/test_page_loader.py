from page_loader.page_loader import download
from page_loader.page_loader import get_filename_for_saving_web_content


def test_download():
    assert download('some_url.com',
                    '/home/paalso/some_path') == '/home/paalso/some_path'


def test_get_filename_for_saving_web_content():
    assert get_filename_for_saving_web_content(
        'https://ru.hexlet.io/courses'
    ) == 'ru-hexlet-io-courses.html'

    assert get_filename_for_saving_web_content(
        'https://ru.hexlet.io'
    ) == 'ru-hexlet-io.html'

    assert get_filename_for_saving_web_content(
        'ru.hexlet.io'
    ) == 'ru-hexlet-io.html'
