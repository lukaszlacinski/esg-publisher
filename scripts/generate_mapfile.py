#!/usr/bin/env python3

import os
import sys
import glob
import hashlib
import uuid
import json


def sha256sum(path):
    with open(path, "rb") as f:
        h = hashlib.file_digest(f, "sha256")
        return h.hexdigest()
    sys.exit(1)


def generate_mapfile(dataset_id, dataset_path, mapfile_path):

    map_list = []
    file_list = glob.glob(dataset_path + "/*.nc")

    for nc_file in file_list:
        stats = os.stat(nc_file)
        mod_time = int(stats.st_mtime)
        checksum = sha256sum(nc_file)
        nc_file_map = [
            dataset_id,
            nc_file,
            f"{stats.st_size}",
            f"mod_time={mod_time}.0",
            f"checksum={checksum}",
            "checksum_type=SHA256"
        ]
        map_list.append(nc_file_map)

    publication_dir = os.path.dirname(mapfile_path)
    os.makedirs(publication_dir, exist_ok=True)

    with open(mapfile_path, "w") as f:
        json.dump(map_list, f)
        print("", file=f)


if __name__ == "__main__":
    '''
    Usage:
        python3.11 generate_mapfile.py <data_root> <relative_dataset_path> <mapfile_path>
    for example
        python3.11 generate_mapfile.py \
            /eagle/projects/ESGF2/esg_dataroot/css03_data \
            CMIP6/AerChemMIP/EC-Earth-Consortium/EC-Earth3-AerChem/hist-piAer/r1i1p1f1/AERday/maxpblz/gn/v20201006 \
            /tmp/mapfile.json
    '''

    dataset_id = "#".join(sys.argv[2].rsplit("/v", 1)).replace("/", ".")
    dataset_path = os.path.join(sys.argv[1], sys.argv[2])
    mapfile_path = sys.argv[3]
    generate_mapfile(dataset_id, dataset_path, mapfile_path)
