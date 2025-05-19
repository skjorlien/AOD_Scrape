import geopandas as gpd
from settings import *
import rasterio
from rasterio.mask import mask
import matplotlib.pyplot as plt
from shapely.geometry import mapping
import pandas as pd
import numpy as np
import os
from datetime import datetime
from tqdm import tqdm

shpfile = f"{Paths.clean_data}/shapefiles/AB617_community_boundaries.shp"
rast = f"{Paths.clean_data}/daily_AOD/2019296_merged.tif"

def get_mean_raster_over_poly(raster_path, polygons: list):
    with rasterio.open(raster_path) as src:
        mean_vals = []
        for poly in polygons:
            geom = [mapping(poly)]
            try: 
                out_image, out_transform = mask(src, geom, crop=True)
                data = out_image[0]
                masked_data = data[data != src.nodata]

                if not np.all(np.isnan(masked_data)):
                    mean_val = data[data != src.nodata].mean()
                else:
                    mean_val = np.nan
            except ValueError as e:
                print(f"{e}")
                mean_val = np.nan
            mean_vals.append(mean_val)
    return mean_vals

def main():
    gdf = gpd.read_file(shpfile)
    gdf = gdf.to_crs("EPSG:4326")

    polys = gdf['geometry'].to_list()
    raster_files = os.listdir(f"{Paths.clean_data}/daily_AOD")
    dates = [datetime.strptime(x[:7], "%Y%j") for x in raster_files]

    output = np.zeros((gdf.shape[0], len(dates)))
    for i, rast in tqdm(enumerate(raster_files), total=len(raster_files)):
        output[:, i] = get_mean_raster_over_poly(f"{Paths.clean_data}/daily_AOD/{rast}", polys)

    meandf = pd.DataFrame(output, index=gdf['id'], columns=dates)
    meandf = meandf.stack().reset_index()
    meandf.columns = ["id", "date", "mean_AOD"]
    meandf.to_csv(f"{Paths.clean_data}/meanAOD.csv")

    
if __name__ == "__main__":
    main()

    
