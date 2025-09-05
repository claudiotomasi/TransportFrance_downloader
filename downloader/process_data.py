# coding: utf-8
import os
import random
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from colorama import Fore, Style
import requests


from downloader.download import download_file
from downloader.extractor import extract_zip_file
from downloader.logger import merge_error_logs

proxies = {
    "http": None,
    "https": None,
}


accepted_formats = ['NeTEx','ods','turtle','parquet','zip','gpx','xml','gpkg','xls','SSIM','gtfs-rt','json','ogc:wfs',
                    'SIRI Lite','png','shp','geojson','web','octet-stream','ogc:wms','html','plain','n3','xlsx','GTFS',
                    'shapefile','gbfs','pdf','pbf','csv.zip','markdown','SIRI','kml','csv']


def process_dataset(ds_id, dataset_attributes, output_folder):
    """Collect all download jobs (url, resource_folder) for a dataset."""
    BASE_URL = f"https://transport.data.gouv.fr/api/datasets/{ds_id}"
    try:
        response = requests.get(BASE_URL, proxy = proxy, timeout=30)
        response.raise_for_status()
        single_ds = response.json()
    except Exception as e:
        return []

    dataset_title = dataset_attributes.loc[
        dataset_attributes["dataset_id"] == ds_id, "title"
    ].values[0]

    dataset_folder = os.path.join(output_folder, dataset_title)
    os.makedirs(dataset_folder, exist_ok=True)

    resources = single_ds.get("resources", [])
    jobs = []

    for res in resources:
        if not res.get("is_available", False):
            continue

        format_file = res.get("format")
        if not format_file or isinstance(format_file, list):
            continue

        if format_file not in accepted_formats:
            continue

        # Create format folder
        format_folder = os.path.join(dataset_folder, format_file)
        os.makedirs(format_folder, exist_ok=True)

        # Subfolder with title + date
        updated_ts = res.get("updated", "")
        try:
            updated_date = datetime.strptime(
                updated_ts, "%Y-%m-%dT%H:%M:%S.%fZ"
            ).strftime("%Y-%m-%d")
        except Exception:
            updated_date = updated_ts[:10]

        resource_folder_name = f"{res.get('title')}_{updated_date}"
        resource_folder = os.path.join(format_folder, resource_folder_name)
        os.makedirs(resource_folder, exist_ok=True)

        url = res.get("original_url")
        if url:
            jobs.append((url, resource_folder))

    return jobs

def collect_jobs(ds_id, dataset_attributes, output_folder):
    """Return download jobs for a single dataset, or empty list if not public-transit."""
    dataset_type = dataset_attributes.loc[
        dataset_attributes["dataset_id"] == ds_id, "type_data"
    ].values[0]

    if dataset_type != "public-transit":
        return []

    return process_dataset(ds_id, dataset_attributes, output_folder)

def start_process(dataset_resources, dataset_attributes, output_folder="./downloads", extract_zip = False, max_workers=4):
    
    if(extract_zip):
        print(f"The extraction of the zip files will happen after the download phase.\n")
    print(f"⚡ Using {max_workers} parallel download threads\n")
    
    os.makedirs(output_folder, exist_ok=True)

    # Get list of dataset IDs
    ds_ids = list(dataset_resources.keys())
    # Shuffle them randomly
    random.shuffle(ds_ids)

    # Parallel collection of download jobs
    download_jobs = []
    # max_workers = min(32, (os.cpu_count() or 1) * 5)  # dynamically choose threads
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(collect_jobs, ds_id, dataset_attributes, output_folder): ds_id for ds_id in ds_ids}
        
        # tqdm for progress
        with tqdm(total=len(ds_ids),
                  desc=Fore.CYAN + Style.BRIGHT + "Collecting jobs" + Style.RESET_ALL,
                  unit="dataset",
                  bar_format="{l_bar}{bar} {n_fmt}/{total_fmt} | Elapsed: {elapsed}") as pbar:
            
            for future in as_completed(futures):
                result = future.result()  # a list of jobs or []
                download_jobs.extend(result)
                pbar.update(1)

    print(f"\n🔗 Total files to download: {len(download_jobs)}")

    zip_files = []
    # Run downloads in parallel with progress bar
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(download_file, url, path, threading.get_ident())
            for url, path in download_jobs
        ]
        with tqdm(
            total=len(futures),
            desc=Fore.CYAN + Style.BRIGHT + "Downloading" + Style.RESET_ALL,
            unit="files",
            bar_format=Fore.MAGENTA + "{l_bar}{bar}" + Style.RESET_ALL + " {n_fmt}/{total_fmt} | Elapsed: {elapsed} | {rate_fmt}{postfix}"
        ) as pbar:
            for future in as_completed(futures):
                _, zip_path = future.result()
                # _ = future.result()  # we ignore ✅/❌ prints here
                if zip_path:
                    zip_files.append(zip_path)
                pbar.update(1)

    
    if extract_zip and zip_files:
        print(f"\n📦 Extracting {len(zip_files)} zip files...")
        extraction_error_log = os.path.join(output_folder, "extraction_errors.log")

        errors = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [
                executor.submit(extract_zip_file, zf, output_folder, threading.get_ident())
                for zf in zip_files
            ]
    
            with tqdm(
                total=len(futures),
                desc=Fore.CYAN + Style.BRIGHT + "Extracting ZIPs" + Style.RESET_ALL,
                unit="files",
                bar_format=Fore.MAGENTA + "{l_bar}{bar}" + Style.RESET_ALL + " {n_fmt}/{total_fmt} | Elapsed: {elapsed} | {rate_fmt}{postfix}"
            ) as pbar:
                for future in as_completed(futures):
                    _, error = future.result()
                    if error:
                        errors.append(error)
                    pbar.update(1)
    
        # Merge all errors into a single log file
        if errors:
            with open(extraction_error_log, "w", encoding="utf-8") as logf:
                logf.write("\n".join(errors))

            
            print(f"\n📄 Extraction errors logged to: {extraction_error_log}. {len(errors)} has been found.")


    print(f"📄 Everything saved in {os.path.abspath(output_folder)}")
    # Merge errors at the end
    merge_error_logs(output_folder) 

