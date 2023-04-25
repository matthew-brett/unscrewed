""" Fetch data from repository, or maybe local cache
"""

from os import environ
from io import StringIO
from pathlib import Path

import yaml

import pooch


class Fetcher:

    def __init__(self, config):
        self.config = self._read_config(config)
        self.registry = self._build_registry(self.config)
        self.data_version = self.config['data_version']

    def _read_config(self, config):
        """ Read configuration from filename, Path, fileobj or mapping.
        """
        if isinstance(config, str):
            config = Path(config)
        if isinstance(config, Path):
            config = StringIO(config.read_text())
        if hasattr(config, 'read'):
            config = yaml.load(config, Loader=yaml.SafeLoader)
        return config

    def _build_registry(self, config):
        """ Build and return Pooch registry object
        """
        return pooch.create(
            # Use the default cache folder for the operating system
            path=pooch.os_cache(config['pkg_name']),
            # The remote data is on Github
            base_url=config.get('base_url', ''),
            version=config.get('data_version'),
            # If this is a development version, get the data from the
            # specified branch (default 'main')
            version_dev=config.get('version_dev', 'main'),
            registry=config.get('files'),
            urls=config.get('urls'),
            # The name of an environment variable that can overwrite the cache
            # path.
            env=config.get('cache_env_var')
        )

    def _from_staging_cache(self, rel_url, staging_cache):
        known_hash = self.registry.registry.get(rel_url)
        if not known_hash:
            return None
        pth = Path(staging_cache).resolve() / self.data_version / rel_url
        action, verb = pooch.core.download_action(pth, known_hash)
        if action == 'update':
            pooch.utils.get_logger().info(
                f"'{rel_url}' in '{staging_cache}/{self.data_version}' "
                "but hash does not match; looking in local cache / registry.")
            return None
        if action == 'fetch':
            return str(pth)

    def __call__(self, rel_url):
        """ Fetch data file from local cache, or registry

        Parameters
        ----------
        rel_url : str
            Location of file to fetch, relative to repository base URLs.  Use
            forward slashes to separate paths, on Windows or Unix.

        Returns
        -------
        local_fname : str
            The absolute path (including the file name) of the file in the local
            storage.
        """
        staging_cache = environ.get(self.config.get('staging_env_var'))
        if staging_cache:
            cache_fname = self._from_staging_cache(rel_url, staging_cache)
            if cache_fname:
                return cache_fname
        return self.registry.fetch(rel_url)
