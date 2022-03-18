""" Fetch data from repository, or maybe local cache
"""

import os
import shutil
from pathlib import Path

import pooch

DATA_VERSION='0.1'


NIPRAXIS_REPO = pooch.create(
    # Use the default cache folder for the operating system
    path=pooch.os_cache("nipraxis"),
    # The remote data is on Github
    base_url="https://raw.githubusercontent.com/nipraxis/nipraxis-data/{version}/",
    version=DATA_VERSION,
    # If this is a development version, get the data from the "main" branch
    version_dev="main",
    registry={
        'ds107_sub012_highres.nii': 'md5:316b0635a4280f65e1ca27ecb34264d6',
        'ds107_sub012_t1r2.nii': 'md5:4546a0a3f7041261b80b56b60cd54126',
        'ds114_sub009_highres.nii': 'md5:95d1b9542a9adebb87e3948c33af478d',
        'ds114_sub009_highres_brain_222.nii': 'md5:615aad84d5b96085601fe306af614564',
        'ds114_sub009_t2r1.nii': 'md5:709fcca8d33ddb7d0b7d501210c8f51c',
        'mni_icbm152_t1_tal_nlin_asym_09a_masked_222.nii': 'md5:6d0615d6581c9f9e17f6916da480fd2e',
        'camera.txt': 'md5:e596928a61c4332252d4eb1f0b6dab1e',
        'ds114_sub009_highres_moved.hdr': 'md5:b12b3d9db549d68b984ace0b95920603',
        'ds114_sub009_highres_moved.img': 'md5:95d1b9542a9adebb87e3948c33af478d',
        'ds114_sub009_t2r1_cond.txt': 'md5:5cb29aed9c9f330afe1af7e69f8aad18',
        'new_cond.txt': 'md5:b40dc95801267932a9f273f02ac05d1e',
        'stimuli.py': 'md5:bced020691fa6408e082e4a1cc090104',
    },
)


#: Path to local cache, if present
LOCAL_CACHE = os.environ.get('NIPRAXIS_LOCAL_CACHE')
if LOCAL_CACHE is not None:
    LOCAL_CACHE = Path(LOCAL_CACHE)


def copy_from_cache(url, output_file, pooch_obj):
    base_url = pooch_obj.base_url
    if not url.startswith(base_url):
        return False
    rel_url = url[len(base_url):]
    pth = LOCAL_CACHE / rel_url
    if not pth.is_file():
        return False
    print('Copying from cache')
    shutil.copyfile(pth, output_file)
    return True


def cache_downloader(url, output_file, pooch_obj):
    """
    Download, checking for local cache
    """
    if LOCAL_CACHE and copy_from_cache(url, output_file, pooch_obj):
        return
    1/0
    pooch.downloaders.choose_downloader(url)(url, output_file, pooch_obj)


def fetch_file(fname):
    """ Fetch data file from registry
    """
    return NIPRAXIS_REPO.fetch(fname, downloader=cache_downloader)
