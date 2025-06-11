#!/bin/bash

INPUT_DIR="./data/raw/archives"
TMP_TIF_DIR="./data/raw/tifs"
OUTPUT_DIR="./data/clean/daily"

mkdir -p "$OUTPUT_DIR" "$TMP_DIF_DIR"

# Step 1: convert all band 1 to tif
for hdf in "$INPUT_DIR"/*.hdf; do
    filename=$(basename "$hdf" .hdf)
    subdataset="HDF4_EOS:EOS_GRID:${hdf}:grid1km:Optical_Depth_055"
    output="$TMP_TIF_DIR/${filename}.tif"
    echo "Processing $hdf → $output"
    gdal_translate -b 1 "$subdataset" "$output"
done


# Step 2: merge all same day tifs into one mosaic
gdal_merge.py -o "merged tif"


# Step 3: Reproject
for tif in "$TMP_TIF_DIR"/*_merged.tif; do
    input=$(basename "$tif" .tif)
    output="$OUTPUT_DIR/${input}.tif"
    gdalwarp -t_srs EPSG:4326 -r near "$tif" "$output"
done

# cleanup
rm -rf "$TMP_TIF_DIR"
