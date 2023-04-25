""" Test local cache
"""

import shutil
from pathlib import Path
from hashlib import sha1

import unscrewed.fetcher as usf
import yaml

import pytest


LOGO_SHA = 'cd8157960cf256e53c4e9722c7c34b8d38eb24ec'
CONFIG_PATH = Path(__file__).parent / 'testreg_registry.yaml'


def test_config_read():
    # config can be any of Path, str filename, stream or dict
    with open(CONFIG_PATH) as fobj:
        config = yaml.load(fobj, Loader=yaml.SafeLoader)
    fetcher = usf.Fetcher(CONFIG_PATH)
    assert fetcher.config == config
    assert fetcher.data_version == config['data_version']
    assert usf.Fetcher(str(CONFIG_PATH)).config == config
    assert usf.Fetcher(config).config == config
    with open(CONFIG_PATH) as fobj:
        assert usf.Fetcher(fobj).config == config


def assert_hash(fname, sha):
    with open(fname, 'rb') as fobj:
        contents = fobj.read()
    assert sha1(contents).hexdigest() == sha


def test_caching(tmp_path, monkeypatch):
    # Test we can use local and staging cache.
    local_cache = tmp_path / 'unscrewed-local'
    staging_cache = tmp_path / 'unscrewed-staging'
    monkeypatch.delenv("TESTREG_STAGING_CACHE", raising=False)
    monkeypatch.setenv("TESTREG_LOCAL_CACHE", str(local_cache))
    fetcher = usf.Fetcher(CONFIG_PATH)
    dv = fetcher.data_version
    fname = 'dsfe_logo.png'
    local_cache_path = local_cache / dv / fname
    out_fname = fetcher(fname)
    assert_hash(out_fname, LOGO_SHA)
    assert Path(out_fname) == local_cache_path
    monkeypatch.setenv("TESTREG_STAGING_CACHE", str(staging_cache))
    out_fname = fetcher(fname)
    assert Path(out_fname) == local_cache_path
    shutil.move(local_cache, staging_cache)
    out_fname = fetcher(fname)
    staging_cache_path = staging_cache / dv / fname
    assert Path(out_fname) == staging_cache_path
    # Delete staging cache version, get local version
    staging_cache_path.unlink()
    assert Path(fetcher(fname)) == local_cache_path
    # Check reload if file present in staging, but hash incorrect.
    staging_cache_path.write_text('Incorrect contents')
    assert Path(fetcher(fname)) == local_cache_path
    # Rewrite file, get from staging path again
    staging_cache_path.write_bytes(local_cache_path.read_bytes())
    assert Path(fetcher(fname)) == staging_cache_path
    # Try fetching a not-known file.
    bad_fname = 'uknown_file.txt'
    with pytest.raises(ValueError):
        fetcher(bad_fname)
    # Fails even if file is in staging and local cache
    Path(local_cache / dv / bad_fname).write_text('Innocuous phrase')
    Path(staging_cache / dv / bad_fname).write_text('Innocuous phrase')
    with pytest.raises(ValueError):
        fetcher(bad_fname)
