""" Fetch data from repository, or maybe local cache
"""

import os
import io
from pathlib import Path

import yaml

import pooch


class Fetcher:

    def __init__(self, config):
        self.config = self._get_config(config)
        self.registry = self._get_registry()

    def _get_config(self, config):
        if isinstance(config, str):
            config = Path(config)
        if isinstance(config, Path):
            config = io.StringIO(config.read_text())
        if hasattr(config, 'read'):
            config = yaml.load(config, Loader=yaml.SafeLoader)
        return config

    def _get_registry(self):
        """ Build and return Pooch image registry object
        """
        config = self.config
        return pooch.create(
            # Use the default cache folder for the operating system
            path=pooch.os_cache(config['pkg_name']),
            # The remote data is on Github
            base_url=config.get('base_url', ''),
            version=config.get('data_version'),
            # If this is a development version, get the data from the "main" branch
            version_dev=config.get('version_dev', 'main'),
            registry=config.get('files'),
            urls=config.get('urls'),
            # The name of an environment variable that can overwrite the cache path.
            env=config.get('cache_env_var')
        )

    def _from_staging_cache(self, rel_url, staging_cache):
        known_hash = self.registry.registry.get(rel_url)
        if not known_hash:
            return None
        data_version = self.config['data_version']
        pth = Path(staging_cache).resolve() / data_version / rel_url
        action, verb = pooch.core.download_action(pth, known_hash)
        if action == 'update':
            pooch.utils.get_logger().info(
                f"'{rel_url}' in '{staging_cache}/{data_version}' "
                "but hash does not match; looking in local cache / registry.")
            return None
        if action == 'fetch':
            return str(pth)

    def fetch_file(self, rel_url):
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
        staging_cache = os.environ.get(self.config.get('staging_env_var'))
        if staging_cache:
            cache_fname = self._from_staging_cache(rel_url, staging_cache)
            if cache_fname:
                return cache_fname
        return self.registry.fetch(rel_url)
