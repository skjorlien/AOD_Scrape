import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling
from rasterio.merge import merge
from pathlib import Path
import re
from config import CLEAN_DATA_DIR, TMP_DIR
import numpy as np


def average_bands(input_paths: list[Path], dst_path: Path, nodata=None) -> tuple[np.ndarray, dict]:
    """
    Average multiple single-band raster files, ignoring nodata values.

    Args:
        file_paths (list[str]): List of single-band TIFF file paths to average.
        nodata (optional): Nodata value to ignore; if None, tries to infer from first file.

    Returns:
        tuple[np.ndarray, dict]: (averaged_array, metadata_dict)
            - averaged_array: 2D numpy array of the average.
            - metadata_dict: metadata copied from the first raster, updated with dtype and nodata.
    """
    if not input_paths:
        raise ValueError("file_paths list is empty")

    arrays = []
    masks = []

    # Open the first file to get metadata and nodata if needed
    with rasterio.open(input_paths[0]) as src0:
        meta = src0.meta.copy()
        if nodata is None:
            nodata = src0.nodata
        # ogshape = src0.shape
        # ogtransform = src0.transform
        # ogcrs = src0.crs

    for fp in input_paths:
        with rasterio.open(fp) as src:
            arr = src.read(1).astype(float)
            mask = (arr == nodata) if nodata is not None else np.zeros(arr.shape, dtype=bool)
            arr[mask] = np.nan
            arrays.append(arr)
            masks.append(~mask)

    stacked = np.stack(arrays)  # shape: (num_files, height, width)

    # Compute average ignoring nan
    avg = np.nanmean(stacked, axis=0)
    avg = np.where(np.isnan(avg), nodata, avg)
    
    # Update metadata for output
    meta.update({
        'driver': 'GTiff',
        'dtype': ('int16'),
        # 'height': ogshape[0],
        # 'width': ogshape[1],
        'count': 1,
        # 'nodata': nodata,
        # 'transform': ogtransform,
        # 'crs': ogcrs
        })

    with rasterio.open(dst_path, 'w', **meta) as dst:
        dst.write(avg, 1)

    return dst_path


def merge_tifs(input_paths: list[Path], dst_path: Path) -> Path:
    '''
    given a list of tifs (i.e., multiple snapshots in a given day),
    merge them into a single raster for that day.

    Args
    file_paths (list[str]): list of paths to merge
    dst_path (str): the location to save

    Returns
    dst_path (str)
    '''
    src_files = [rasterio.open(fp) for fp in input_paths]
    merged_array, merged_transform = merge(src_files)
    merged_array = merged_array[0]

    kwargs = src_files[0].meta.copy()
    kwargs.update({
        'driver': 'GTiff',
        'height': merged_array.shape[0],
        'width': merged_array.shape[1],
        'transform': merged_transform,
        'count': 1
    })

    fpath = input_paths[0].parent
    date = re.search(r'\.A(\d{7})\.', input_paths[0].name).group(1)
    fname = f"{date}_merged.tif"
    dst_path = fpath / fname

    with rasterio.open(dst_path, 'w', **kwargs) as dst:
        dst.write(merged_array, 1)

    for src in src_files:
        src.close()

    return dst_path


def reproject_tif(input_path: Path, dst_path: Path, target_crs: str = "EPSG:4326"):
    '''
    given a path to a tiff, reproject it to the target crs.

    Args:
    src_path (str): the file to process
    dst_path (str): the location to save
    target_crs (str): the coordinate reference system that you want to export

    Returns
    dst_path (str)
    '''
    with rasterio.open(f"{input_path}") as src:
        transform, width, height = calculate_default_transform(src.crs,
                                                               target_crs,
                                                               src.width,
                                                               src.height,
                                                               *src.bounds)
        kwargs = src.meta.copy()
        kwargs.update({
            'crs': target_crs,
            'transform': transform,
            'width': width,
            'height': height
        })
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


def main():
    BAND_DIR = TMP_DIR / "bands"

    print("Generating list of band files for same base name (multiple bands per hdf)")
    file_stems = list(set([f.stem.split("_band")[0] for f in BAND_DIR.iterdir()]))
    band_lists = [[f for f in BAND_DIR.iterdir() if stem in f.name] for stem in file_stems]

    print("Averaging bands of a given hdf")
    averaged_tifs = [average_bands(bands, TMP_DIR / f"{stem}.tif") for stem, bands in zip(file_stems, band_lists)]

    print("Generating list of averaged tifs per day of scraped data (multiple hdfs per day)")
    dates = set([re.search(r'\.A(\d{7})\.', stem).group(1) for stem in file_stems])
    date_files = [[f for f in averaged_tifs if date in f.name] for date in dates]

    print("Merging and reprojecting into one file per day")
    merged_files = [merge_tifs(files, TMP_DIR / f"{date}.tif") for files, date in zip(date_files, dates)]

    reprojected_files = [reproject_tif(file, CLEAN_DATA_DIR / f"{date}.tif") for file, date in zip(merged_files, dates)]

    return reprojected_files


if __name__ == "__main__":
    main()
