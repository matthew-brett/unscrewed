""" Unscrewed data packaging

The key function is ``fetch_file``; this fetches data from the unscrewed data
repository, caching in a known location to avoid repeat downloads.

"""

__version__ = '0.1a2'

from .fetcher import Fetcher
