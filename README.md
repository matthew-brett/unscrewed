# Unscrewed

Utility for making and updating a data fetcher component of your project.

## Install

```bash
pip install unscrewed
```

## Usage

First prepare a `registry.yaml` file, like the one in
`unscrewed/tests/nipraxis_registry.yaml`.  Put it in your package, say in the
`your_package` directory (that contains the `__init__.py` file.  Maybe call it
`registry.yaml`.

In some module, say `your_package/data.py`

```python
import pkg_resources

import unscrewed

_config_file = pkg_resources.resource_filename("your_package", "registry.yaml")
_fetcher = unscrewed.Fetcher(_config_file)
fetch_file = _fetcher.fetch_file
```

Say you have a file `my_data_file.nii` configured in your `registry.yaml` file above.

Now you can fetch it like this:

```python
from your_package.data import fetch_file

fname = fetch_file('my_data_file.nii')
```
