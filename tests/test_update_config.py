""" Test updating config
"""

from pathlib import Path

from unscrewed.update_config import (
    update_config,
    RepoError,
    url2cloneable,
    check_add_repo,
    cloneable2out_sdir,
)
import unscrewed.fetcher as usf

import pytest


CONFIG_PATH = Path(__file__).parent / 'testreg_registry.yaml'


def test_config(tmp_path):
    config = usf.Fetcher(CONFIG_PATH).config
    new_config = update_config(config, tmp_path)
    assert config == new_config


def test_url2cloneable():
    base_url = ("https://raw.githubusercontent.com/"
                "matthew-brett/unscrewed/{version}/tests/testreg")
    assert url2cloneable(base_url) == (
        'https://github.com/matthew-brett/unscrewed',
        '{version}',
        'tests/testreg')
    with pytest.raises(RepoError):
        url2cloneable('git' + base_url[5:])


def test_check_add_repo(tmp_path):
    base_url = ("https://raw.githubusercontent.com/"
                "matthew-brett/unscrewed/{version}/tests/testreg")
    with pytest.raises(RepoError):
        check_add_repo(base_url.replace('{version}', '0.3a1'),
                       '0.1a2',
                       tmp_path)
    with pytest.raises(RepoError):
        check_add_repo(base_url,
                       None,
                       tmp_path)
    out_path, rel_path = check_add_repo(base_url,
                                        '0.1a2',
                                        tmp_path)
    assert out_path.is_dir()
    assert rel_path == 'tests/testreg'


def test_cloneable2out_dir():
    assert cloneable2out_sdir('https://foo.bar/baz') == 'baz'
    assert cloneable2out_sdir('https://foo.bar/baz/') == 'baz'
    assert cloneable2out_sdir('https://foo.bar/baz.git') == 'baz'
    assert cloneable2out_sdir('https://foo.bar/baz/boo.git') == 'boo'
    assert cloneable2out_sdir('https://foo.bar/baz/boo.git/') == 'boo'
