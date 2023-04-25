""" Update configuration file for data repository
"""

from argparse import ArgumentParser, RawDescriptionHelpFormatter

import yaml

from .fetcher import Fetcher

def update_config(config, repo_dir=None):
    config = Fetcher(config).config
    # Look for cloned version of repository.
    # Check repo is clean, pushed.
    # Get current branch, put into config['version_dev']
    # Get current commit, put into config['data_version']
    # Calculate hashes for each file not ignored.
    # Insert in config['files']
    # Consider checking external files.
    return config


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
