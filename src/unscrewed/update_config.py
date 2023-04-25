""" Update configuration file for data repository
"""

from argparse import ArgumentParser, RawDescriptionHelpFormatter

import yaml

from .fetcher import Fetcher


def update_config(config, repo_url,
                  repo_dir=None,
                  external_dir=None,
                  default_hasher='md5'):
    config = Fetcher(config).config
    repo_dir = get_check_repo(config, repo_url, repo_dir)
    # Calculate hashes for each file not ignored, set
    config['files'], config['urls'] = calc_hashes(config, repo_dir,
                                                  external_dir,
                                                  default_hasher)
    # Consider checking external files.
    return config


def get_check_repo(config, repo_url, repo_dir):
    # If repo_dir is None, clone data repository to tempory
    # Look for cloned version of repository.
    # Check repo is clean, pushed.
    return repo_dir


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
    parser.add_argument('-d', '--repo-dir',
                        help='Directory in which to clone repositories')
    return parser


def cli():
    parser = get_parser()
    args = parser.parse_args()
    config = update_config(args.config_fname, repo_dir=args.repo_dir)
    write_config(config, args.config_fname)
