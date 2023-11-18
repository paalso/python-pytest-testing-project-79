from page_loader.url_utils import (
    netloc,
    filename_from_url,
    extension,
    dirname_for_web_resources,
    scheme,
    full_url,
)


def test_filename_from_url():
    assert (filename_from_url("assets/img/omelette.png")
            == "assets-img-omelette.png")

    assert (filename_from_url("/assets/img/omelette.png")
            == "assets-img-omelette.png")

    assert (
        filename_from_url("https://lorem.dot.net/assets/omelette.html")
        == "lorem-dot-net-assets-omelette.html"
    )

    assert (
        filename_from_url("http://lorem.dot.net/assets/omelette")
        == "lorem-dot-net-assets-omelette.html"
    )

    assert (
        filename_from_url("http://lorem.dot.net/assets/omelette/")
        == "lorem-dot-net-assets-omelette.html"
    )


def test_dirname_for_web_resources():
    assert (
        dirname_for_web_resources("paalso-github-io-web_page.html")
        == "paalso-github-io-web_page_files"
    )
    assert (
        dirname_for_web_resources(
            "paalso-github-io-web_page.html", "resources")
        == "paalso-github-io-web_page_resources"
    )


def test_full_url():
    assert (
        full_url("https://lorem.dot.net", "assets/omelette.html")
        == "https://lorem.dot.net/assets/omelette.html"
    )
    assert (
        full_url("https://lorem.dot.net",
                 "https://img.freepik.com/illustration.jpg")
        == "https://img.freepik.com/illustration.jpg"
    )


def test_scheme():
    assert scheme("lorem/assets/professions/python.png") == ""
    assert scheme("https://lorem.dot.net/assets/python.png") == "https"


def test_netloc():
    assert netloc("lorem/assets/professions/python.png") == ""
    assert (
        netloc("https://lorem.dot.net/professions/assets/python.png")
        == "lorem.dot.net"
    )


def test_extension():
    assert extension("https://lorem.dot.net/lib/bio.dhtml") == "dhtml"
    assert extension("https://lorem.dot.net/some_web_page/") == ""
