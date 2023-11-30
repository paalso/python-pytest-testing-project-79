# tests/test_path_processor.py
import pytest
from bs4 import BeautifulSoup
from page_loader.resource_processor import ResourceProcessor

resource_tags = {
    'img': 'src',
    'link': 'href',
    'script': 'src',
}

all_possible_urls = [
    'https://ru.hexlet.io/courses/',
    'https://ru.hexlet.io/courses',
    'https://ru.hexlet.io/courses/index.html'
]


@pytest.fixture
def path_processor(url):
    rp = ResourceProcessor(url, resource_tags, 'some_path')
    return rp


@pytest.fixture
def image_resource():
    img_tag = '<img alt="Some alt text" src="img/some_image.png"/>'
    soup = BeautifulSoup(img_tag, 'html.parser')
    resource = soup.find('img')
    return resource


'''
@pytest.mark.parametrize(
    'url', ['https://ru.hexlet.io/courses/', 'https://ru.hexlet.io/courses'])
def test_path_processor_paths_attributes(path_processor):
    assert path_processor.path_to_save_page_content == os.path.join(
        'some_path', 'ru-hexlet-io-courses.html')
    assert path_processor.__resources_path == os.path.join(
        'some_path', 'ru-hexlet-io-courses_files')


@pytest.mark.parametrize('url', ['https://ru.hexlet.io/courses/main.html'])
def test_path_processor_paths_attributes2(path_processor):
    assert path_processor.path_to_save_page_content == os.path.join(
        'some_path', 'ru-hexlet-io-courses-main.html')
    assert path_processor.__resources_path == os.path.join(
        'some_path', 'ru-hexlet-io-courses-main_files')


@pytest.mark.parametrize('url', all_possible_urls)
def test_get_resource_link_attr(path_processor, image_resource):
    assert path_processor.__get_resource_link_attr(image_resource) == 'src'


@pytest.mark.parametrize('url', all_possible_urls)
def test_get_resource_url(path_processor, image_resource):
    assert (path_processor.__get_resource_url(image_resource)
            == 'img/some_image.png')


@pytest.mark.parametrize('url', all_possible_urls)
def test_get_recourse_full_url(path_processor):
    resource_url = 'https://ru.hexlet.io/courses/assets/python.png'
    assert (path_processor.__get_resource_full_url(resource_url)
            == 'https://ru.hexlet.io/courses/assets/python.png')

    resource_url = 'https://js.stripe.com/v3/js/runtime.js'
    assert (path_processor.__get_resource_full_url(resource_url)
            == 'https://js.stripe.com/v3/js/runtime.js')

    resource_url = '/assets/professions/python.png'
    assert (path_processor.__get_resource_full_url(resource_url)
            == 'https://ru.hexlet.io/assets/professions/python.png')

    resource_url = 'assets/professions/python.png'
    assert (path_processor.__get_resource_full_url(resource_url)
            == 'https://ru.hexlet.io/courses/assets/professions/python.png')


def test_make_resources_dir(tmp_path):
    pp = PathProcessor('https://example.com', resource_tags, path=tmp_path)
    assert not os.path.exists(pp.__resources_path)
    pp.make_resources_dir()
    assert os.path.exists(pp.__resources_path)
    assert os.path.isdir(pp.__resources_path)


@pytest.mark.parametrize(
    'url',
    ['https://ru.hexlet.io/courses/', 'https://ru.hexlet.io/courses'])
def test_get_resource_updated_link1(path_processor):
    resource_url = 'http://ru.hexlet.io/courses/assets/professions/python.png'
    result = path_processor.__get_resource_updated_link(resource_url)
    assert (result == 'ru-hexlet-io-courses_files/'
                      'ru-hexlet-io-courses-assets-professions-python.png')


@pytest.mark.parametrize('url', ['https://ru.hexlet.io/courses/main.html'])
def test_get_resource_updated_link2(path_processor):
    resource_url = 'http://ru.hexlet.io/courses/assets/professions/python.png'
    result = path_processor.__get_resource_updated_link(resource_url)
    assert (result == 'ru-hexlet-io-courses-main_files/'
                      'ru-hexlet-io-courses-assets-professions-python.png')


@pytest.mark.parametrize(
    'url',
    ['https://ru.hexlet.io/courses/', 'https://ru.hexlet.io/courses'])
def test_get_path_to_save_recourse1(path_processor):
    resource_url = 'http://ru.hexlet.io/courses/assets/professions/python.png'
    result = path_processor.__get_path_to_save_resource(resource_url)
    assert (result == 'some_path/ru-hexlet-io-courses_files/'
                      'ru-hexlet-io-courses-assets-professions-python.png')


@pytest.mark.parametrize(
    'url', ['https://ru.hexlet.io/courses/main.html'])
def test_get_path_to_save_recourse2(path_processor):
    resource_url = 'http://ru.hexlet.io/courses/assets/professions/python.png'
    result = path_processor.__get_path_to_save_resource(resource_url)
    assert result == ('some_path/ru-hexlet-io-courses-main_files/'
                      'ru-hexlet-io-courses-assets-professions-python.png')


@pytest.mark.parametrize('url', all_possible_urls)
def test_is_other_domain(path_processor):
    resource_url = 'http://ru.hexlet.io/courses/assets/professions/python.png'
    assert not path_processor.__is_other_domain(resource_url)

    resource_url = '/assets/professions/python.png'
    assert not path_processor.__is_other_domain(resource_url)

    resource_url = 'assets/professions/python.png'
    assert not path_processor.__is_other_domain(resource_url)

    resource_url = 'http://ru.hrexlet.io/assets/professions/python.png'
    assert path_processor.__is_other_domain(resource_url)
'''
