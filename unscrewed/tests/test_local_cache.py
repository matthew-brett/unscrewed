""" Test local cache
"""

import shutil
from hashlib import sha1

import unscrewed.fetcher as npxf

CAMERA_HASH = 'af7257977f30797d4b3ea7dd15fa362d4fe8c37e'


def assert_hash(fname, hash):
    with open(fname, 'rb') as fobj:
        contents = fobj.read()
    assert sha1(contents).hexdigest() == hash


def test_camera(tmp_path, monkeypatch):
    local_cache = tmp_path / 'unscrewed-local'
    staging_cache = tmp_path / 'unscrewed-staging'
    monkeypatch.delenv("NIPRAXIS_STAGING_CACHE", raising=False)
    monkeypatch.setenv("NIPRAXIS_LOCAL_CACHE", str(local_cache))
    fetcher = npxf.Fetcher(npxf._CONFIG)
    monkeypatch.setattr('unscrewed.fetcher.fetch_file', fetcher.fetch_file)
    fname = npxf.fetch_file('camera.txt')
    assert fname.startswith(str(local_cache))
    monkeypatch.setenv("NIPRAXIS_STAGING_CACHE", str(staging_cache))
    fname = npxf.fetch_file('camera.txt')
    assert fname.startswith(str(local_cache))
    shutil.move(local_cache, staging_cache)
    fname = npxf.fetch_file('camera.txt')
    assert fname.startswith(str(staging_cache))
