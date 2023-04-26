""" Update configuration file for data repository
"""

from argparse import ArgumentParser, RawDescriptionHelpFormatter
from urllib.parse import urlparse
from subprocess import check_call, check_output
from tempfile import TemporaryDirectory
from pathlib import Path

import yaml

from .fetcher import Fetcher


def update_config(config,
                  repos_path,
                  default_hasher='md5'):
    config = Fetcher(config).config
    file_defs = get_file_defs(config)
    repos_path.mkdir(parents=True, exist_ok=True)
    return config   # For now.
    check_add_repos(file_defs, repos_path)
    fill_check_hashes(file_defs, default_hasher)
    fill_config(config, file_defs)
    return config

def get_file_defs(config):
    return config['files']


def check_add_repos(file_defs, repos_path):
    for fname, info in file_defs.items():
        # Modify dictionary in-place.
        info['repo_path'], info['rel_path'] = check_add_repo(
            info['url'],
            info['version'],
            repos_path)


class RepoError(ValueError):
    """ Signal error analyzing repository URL """


def check_add_repo(url, version, repos_path):
    cloneable, url_version, relpath = url2cloneable(url)
    if cloneable is None:
        return None, None
    if version:
        if url_version != '{version}':
            raise RepoError(
                f'Requested version is {version} but URL has {url_version}')
        url_version = version
    elif url_version == '{version}':
        raise RepoError(
            f'No requested version, but URL {url} contains'
            '{version}')
    return check_clone(cloneable, url_version, repos_path), relpath


def check_clone(cloneable, version, repos_path):
    out_path = repos_path / cloneable2out_sdir(cloneable)
    if out_path.is_dir():
        check_repo_at_commit(out_path, version)
    else:
        check_call(['git', 'clone', cloneable, str(out_path)])
    return out_path


def check_repo_at_commit(out_path, version):
    desired_commit = check_output(
        ['git', 'rev-parse', version],
        cwd=out_path, text=True)
    actual_commit = check_output(
        ['git', 'rev-parse', 'HEAD'],
        cwd=out_path, text=True)
    if not desired_commit == actual_commit:
        raise RepoError(
            f'repo at {out_path} at commit {actual_commit}'
            f'but should be at {desired_commit}')
    status = check_output(
        ['git', 'status', '--porcelain'],
        cwd=out_path, text=True).strip()
    if status:
        raise RepoError(
            f'repo at {out_path} not clean with status {status}')


def cloneable2out_sdir(cloneable):
    out_sdir = [p for p in cloneable.split('/') if p][-1]
    if out_sdir.endswith('.git'):
        out_sdir = out_sdir[:-4]
    return out_sdir


def url2cloneable(url):
    parts = urlparse(url)
    if parts.scheme != 'https':
        raise RepoError(f'Need https: scheme, but URL is {url}')
    if parts.netloc == 'raw.githubusercontent.com':
        # Github raw file.
        fparts = parts.path.split('/')
        return ('https://github.com' + '/'.join(fparts[:3]),
                fparts[3],
                '/'.join(fparts[4:]))
    return None, None, None


def calc_hashes(config, repo_dir, external_dir=None, default_hasher='md5'):
    return config['files'], config.get('urls')


def write_config(config, fname):
    with open(fname, 'wt') as fobj:
        yaml.dump(config, fobj, sort_keys=False)


def get_parser():
    parser = ArgumentParser(description=__doc__,  # Usage from docstring
                            formatter_class=RawDescriptionHelpFormatter)
    parser.add_argument('config_fname',
                        help='Configuration filename')
    parser.add_argument('-d', '--repos-dir',
                        help='Directory in which to clone repositories')
    return parser


def cli():
    parser = get_parser()
    args = parser.parse_args()
    if args.repos_dir is None:
        args.repos_dir = Path(TemporaryDirectory().name)
    config = update_config(args.config_fname, repos_dir=args.repos_dir)
    write_config(config, args.config_fname)
