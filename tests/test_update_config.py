""" Test updating config
"""

from pathlib import Path

import unscrewed.update_config as usu
import unscrewed.fetcher as usf


CONFIG_PATH = Path(__file__).parent / 'testreg_registry.yaml'


def test_config():
    config = usf.Fetcher(CONFIG_PATH).config
    new_config = usu.update_config(config, None)
    assert config == new_config
