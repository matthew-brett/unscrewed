""" Test local cache
"""

import shutil
from pathlib import Path
from hashlib import sha1

import unscrewed.fetcher as usf


LOGO_SHA = 'cd8157960cf256e53c4e9722c7c34b8d38eb24ec'


def assert_hash(fname, sha):
    with open(fname, 'rb') as fobj:
        contents = fobj.read()
    assert sha1(contents).hexdigest() == sha


def test_camera(tmp_path, monkeypatch):
    local_cache = tmp_path / 'unscrewed-local'
    staging_cache = tmp_path / 'unscrewed-staging'
    monkeypatch.delenv("TESTREG_STAGING_CACHE", raising=False)
    monkeypatch.setenv("TESTREG_LOCAL_CACHE", str(local_cache))
    config = Path(__file__).parent / 'testreg_registry.yaml'
    fetcher = usf.Fetcher(config)
    fname = fetcher('dsfe_logo.png')
    assert_hash(fname, LOGO_SHA)
    assert fname.startswith(str(local_cache))
    monkeypatch.setenv("TESTREG_STAGING_CACHE", str(staging_cache))
    fname = fetcher('dsfe_logo.png')
    assert fname.startswith(str(local_cache))
    shutil.move(local_cache, staging_cache)
    fname = fetcher('dsfe_logo.png')
    assert fname.startswith(str(staging_cache))
