#!/bin/bash

INPUT_DIR="./data/raw/archives"
BAND_DIR="./data/tmp/bands"
OUTPUT_DIR="./data/clean/daily"

mkdir -p "$BAND_DIR"

echo "Extracting bands from HDF"

for hdf in "$INPUT_DIR"/*.hdf; do
    filename=$(basename "$hdf" .hdf)
    subdataset="HDF4_EOS:EOS_GRID:${hdf}:grid1km:Optical_Depth_055"
    band_count=$(gdalinfo "$subdataset" | grep -c "^Band ") 

    band_inputs=""
    for ((i=1; i<=band_count; i++)); do
	band_tif="$BAND_DIR/${filename}_band${i}.tif"
	gdal_translate -q -b $i "$subdataset" "$band_tif"
	band_inputs="$band_inputs -A $i=$band_tif"
    done
done

source venv/bin/activate
cd src
python -m process_hdf
cd ..
deactivate

rm -rf "./data/tmp"
