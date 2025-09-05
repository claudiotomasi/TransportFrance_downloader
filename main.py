#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import os
import requests
from datetime import datetime
import pandas as pd
import time

from downloader.process_data import start_process
from downloader.utils import get_max_workers


    
parser = argparse.ArgumentParser(description="Download datasets with optional ZIP extraction.")
parser.add_argument(
    "-zip", "--extract-zip",
    action="store_true",   # becomes True if provided
    help="If set, extract ZIP files after download."
)
parser.add_argument(
    "-t", "--max-threads",
    type=int,
    help="If not set, the tool will automatically set the #threas as high as possible."
)
parser.add_argument(
        "-o", "--output-directory",
        type=str,
        default="./downloads",
        help="Directory where downloaded files will be saved (default: ./downloads)."
)
args = parser.parse_args()

extract_zip = args.extract_zip
max_workers = args.max_threads
output_folder = args.output_directory

# output_folder = "./downloads"
os.makedirs(output_folder, exist_ok=True)

BASE_URL = "https://transport.data.gouv.fr/api/datasets"
response = requests.get(BASE_URL)
response.raise_for_status()
dataset = response.json()

print("Number of datasets returned:", len(dataset))

dataset_resources = {}
dataset_attributes = []
for ds in dataset:
    ds_id = ds.get("id")
    resources = ds.get("resources", [])
    dataset_resources[ds_id] = [res.get("id") for res in resources if "id" in res]

    dataset_attributes.append(
        {
            "dataset_id": ds_id,
            "title": ds.get("title"),
            "updated": datetime.strptime(
                ds["updated"], "%Y-%m-%dT%H:%M:%S.%fZ"
            ).date()
            if ds.get("updated")
            else None,
            "page_url": ds.get("page_url"),
            "type_data": ds.get("type"),
        }
    )

df_attributes = pd.DataFrame(dataset_attributes)
if not max_workers:
    max_workers = get_max_workers()

start_time = time.time()  # start timer
start_process(dataset_resources, df_attributes, output_folder, extract_zip, max_workers)

end_time = time.time()  # end timer
total_seconds = end_time - start_time
mins, secs = divmod(int(total_seconds), 60)

print(f"✅ Download complete. Total time: {mins}m {secs}s")

