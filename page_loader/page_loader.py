from .download_manager import DownloadManager


def download(url, path=None):
    manager = DownloadManager(url, path or '')
    return manager.download()
