from page_loader.hello import hello


def test_hello():
    assert hello() == 'Hello!'
