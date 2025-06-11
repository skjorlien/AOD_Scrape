import os
import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling
from rasterio.merge import merge
from pprint import pprint
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
from time import time
import geopandas as gpd
from rasterio.plot import show
from tqdm import tqdm
import re
from concurrent.futures import ProcessPoolExecutor, as_completed
from config import RAW_DATA_DIR, CLEAN_DATA_DIR

RAW_PATH = RAW_DATA_DIR / "archives"
TMP_PATH = CLEAN_DATA_DIR / "tmpTiff"
CLEAN_PATH = CLEAN_DATA_DIR
PREFIX = "HDF4_EOS:EOS_GRID:"
SUFFIX = ":grid1km:Optical_Depth_055"


def generate_tif(src_path: str, dst_path: str) -> str:
    '''
    Given an hdf file path, average all bands and save a one-banded geotiff

    Args:
    src_path (str): path to hdf to process
    dst_path (str): path to save geotiff
    '''
    with rasterio.open(f"{src_path}") as ds:
        # manage the missing data marker. numpy wants it to be nan but geotiff wants it to be some number. Need to carefully convert
        missing = ds.nodata

        # separate out the bands
        bands = np.array([ds.read(i+1) for i in range(ds.count)])
        bands = np.nan_to_num(bands, nan=missing)

        if missing is not None:
            bands = np.where(bands == missing, np.nan, bands)

        data = np.nanmean(bands, axis=0)
        data = np.where(np.isnan(data), missing, data)
        with rasterio.open(f'{dst_path}', 'w', driver='GTiff', height=ds.height, width=ds.width,
                           count=1, dtype=('int16'), crs=ds.crs, transform=ds.transform, nodata=missing) as dst:
            dst.write(data, 1)
    return dst_path


def reproject_tif(src_path: str, dst_path: str, target_crs: str="EPSG:4326"):
    '''
    given a path to a tiff, reproject it to the target crs.

    Args:
    src_path (str): the file to process
    dst_path (str): the location to save
    target_crs (str): the coordinate reference system that you want to export

    Returns
    dst_path (str)
    '''
    with rasterio.open(f"{src_path}") as src:
        transform, width, height = calculate_default_transform(src.crs, target_crs, src.width, src.height, *src.bounds)
        kwargs = src.meta.copy()
        kwargs.update({'crs': target_crs, 'transform': transform, 'width': width, 'height': height})
        with rasterio.open(dst_path, 'w', **kwargs) as dst:
            reproject(
                source=rasterio.band(src, 1),
                destination=rasterio.band(dst, 1),
                src_transform=src.transform,
                src_crs=src.crs,
                dst_transform=transform,
                dst_crs=target_crs,
                resampling=Resampling.nearest)
    return dst_path


def merge_tifs(file_paths: list[str], dst_path: str) -> str:
    '''
    given a list of tifs (i.e., multiple snapshots in a given day), merge them into a single raster for that day.

    Args
    file_paths (list[str]): list of paths to merge
    dst_path (str): the location to save

    Returns
    dst_path (str)
    '''
    src_files = [rasterio.open(fp) for fp in file_paths]
    src = src_files[0]
    
    merged_array, merged_transform = merge(src_files)
    merged_array = np.squeeze(merged_array)
    kwargs = src.meta.copy()
    kwargs.update({
        'driver': 'GTiff',
        'height': merged_array.shape[0],
        'width': merged_array.shape[1],
        'transform': merged_transform
    })
    with rasterio.open(dst_path, 'w', **kwargs) as dst:
        dst.write(merged_array, 1)
    return dst_path


def process_date(date):
    '''
    process all hdf files pertaining to a given date.

    Args
    date (str): the date to process in YYYYDDD format

    Returns
    None
    '''
    # get all relevant files in the raw dir.
    files = [os.path.join(RAW_PATH, x) for x in os.listdir(RAW_PATH) if date in x]
    file_paths = [f"{PREFIX}{fname}{SUFFIX}" for fname in files]
    tif_paths = [f"{TMP_PATH}/{date}_{i:02}.tif" for i in range(len(files))]
    reproject_paths = [f"{TMP_PATH}/{date}_epsg_{i:02}.tif" for i in range(len(tif_paths))]
    
    # step 1. convert these files to my initial tif.
    [generate_tif(src_path, dst_path) for src_path, dst_path in zip(file_paths, tif_paths)]

    # step 2. reproject these files
    [reproject_tif(src_path, dst_path) for src_path, dst_path in zip(tif_paths, reproject_paths)]

    # step 3. merge these files
    dst_path = f"{CLEAN_PATH}/daily_AOD/{date}_merged.tif"
    merge_tifs(reproject_paths, dst_path)

    # clear all tmp files pertaining to this date
    tmp_files = [os.path.join(TMP_PATH, x) for x in os.listdir(TMP_PATH) if date in x]
    [os.remove(fpath) for fpath in tmp_files]


class HDFFile:
    def __init__(self, hdf_file: Path):
        self.hdf_file = hdf_file
        self.path = f"{PREFIX}{self.hdf_file.as_posix()}{SUFFIX}"
        self.tif_path = TMP_PATH

class AODDay:
    def __init__(self, date, hdf_files):
        self.date = date
        self.hdf_files = hdf_files

    @classmethod
    def from_date(cls, date, path: Path = RAW_PATH):
        try:
            files = [f for f in path.iterdir() if date in f.name and "hdf" in f.suffix]
            if len(files) == 0:
                raise ValueError

        except ValueError:
            print("There were no files matching this date.. Can't construct AODDay")

        return cls(date, files)

    
def main():
    '''
    process all dates found in the RAWPATH (the location of saving the scraped files).
    '''
    dates = sorted(set(re.findall(r'\.A(\d{7})\.', " ".join(os.listdir(RAW_PATH)))))

    progress_bar = tqdm(total=len(dates))

    with ProcessPoolExecutor() as executor:
        futures = [executor.submit(process_date, date) for date in dates]
        for _ in as_completed(futures):
            progress_bar.update(1)


if __name__ == "__main__":
    main()
