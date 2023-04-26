""" Test updating config
"""

from pathlib import Path
from subprocess import check_call, check_output

from unscrewed.update_config import (
    update_config,
    RepoError,
    url2cloneable,
    check_add_repo,
    cloneable2out_sdir,
    check_clone
)
import unscrewed.fetcher as usf

import pytest


CONFIG_PATH = Path(__file__).parent / 'testreg_registry.yaml'

BASE_URL = ("https://raw.githubusercontent.com/"
            "matthew-brett/unscrewed/{version}/tests/testreg")
BASE_REPO = 'https://github.com/matthew-brett/unscrewed'


def test_config(tmp_path):
    config = usf.Fetcher(CONFIG_PATH).config
    new_config = update_config(config, tmp_path)
    assert config == new_config


def test_url2cloneable():
    assert url2cloneable(BASE_URL) == (
        'https://github.com/matthew-brett/unscrewed',
        '{version}',
        'tests/testreg')
    with pytest.raises(RepoError):
        url2cloneable('git' + BASE_URL[5:])


def test_check_add_repo(tmp_path):
    with pytest.raises(RepoError):
        check_add_repo(BASE_URL.replace('{version}', '0.3a1'),
                       '0.1a2',
                       tmp_path)
    with pytest.raises(RepoError):
        check_add_repo(BASE_URL,
                       None,
                       tmp_path)
    out_path, rel_path = check_add_repo(BASE_URL,
                                        '0.1a2',
                                        tmp_path)
    assert out_path.is_dir()
    assert rel_path == 'tests/testreg'


def test_check_clone(tmp_path):
    version = '0.1a2'
    out_path = check_clone(BASE_REPO, version, tmp_path)
    assert out_path.is_dir()
    check_call(['git', 'checkout', 'HEAD~1', '-q'], cwd=out_path)
    with pytest.raises(RepoError):
        check_clone(BASE_REPO, version, tmp_path)
    # Reset to correct correct - no error.
    check_call(['git', 'checkout', version], cwd=out_path)
    print(check_output(['git', 'status'], cwd=out_path, text=True))
    check_clone(BASE_REPO, version, tmp_path)
    # Set to dirty.
    bad_file = out_path / 'bad_file.txt'
    bad_file.write_text('Some text')
    with pytest.raises(RepoError):
        check_clone(BASE_REPO, version, tmp_path)
    # Delete bad file, runs without error.
    bad_file.unlink()
    check_clone(BASE_REPO, version, tmp_path)


def test_cloneable2out_dir():
    assert cloneable2out_sdir('https://foo.bar/baz') == 'baz'
    assert cloneable2out_sdir('https://foo.bar/baz/') == 'baz'
    assert cloneable2out_sdir('https://foo.bar/baz.git') == 'baz'
    assert cloneable2out_sdir('https://foo.bar/baz/boo.git') == 'boo'
    assert cloneable2out_sdir('https://foo.bar/baz/boo.git/') == 'boo'
