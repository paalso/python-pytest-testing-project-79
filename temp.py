from page_loader import download


def main():
    url = "https://deti-online.com/skazki/russkie-narodnye-skazki/kolobok/"
    url = "https://paalso.github.io/a-plus/"
    url = "https://lib.misto.kiev.ua/HAJAM/bio.dhtml"
    url = "https://paalso.github.io/simple_web_page/"

    result = download(url, 'temp')
    print(result)


if __name__ == '__main__':
    main()
