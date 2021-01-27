"""tests for photo_downloader/settings.py"""
import os

from photo_downloader import settings


def test_fix_path():
    """test function fix_path"""
    rel_path = settings.fix_path("../tests/test_settings.py")
    script_path = os.path.normpath(__file__)
    assert script_path == rel_path, "fix_path is not resolving the correct path"


def test_get_config():
    """test function get_config"""
    cfg = settings.get_config()
    assert cfg

    flickr_api_key = cfg.get('flickr.api_key')
    assert flickr_api_key, "flickr.api_key missing"

    flickr_api_secret = cfg.get('flickr.api_secret')
    assert flickr_api_secret, "flickr.api_secret missing"
