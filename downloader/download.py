import os
import requests
import zipfile
from .utils import sanitize_filename
from .utils import get_filename_from_cd


proxies = {
    "http": None,
    "https": None,
}

def download_file(url, resource_folder, thread_id):
    """Download a single file and return success/error message."""

    headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36"
    }

    zip_path = None
    try:
        with requests.get(url, proxies = proxies, stream=True, headers = headers, timeout=60) as r:
            # cd = r.headers.get("Content-Disposition")
            # if cd and "filename=" in cd:
            #     filename = cd.split("filename=")[1].strip('"')
            # else:
            #     # maybe the request has a redirected link!
            #     filename = os.path.basename(r.url)
                # filename = os.path.basename(url)
            cd = r.headers.get("Content-Disposition")
            filename = get_filename_from_cd(cd)
        
            if not filename:
                # fallback: last part of URL
                filename = os.path.basename(r.url)
            filename = sanitize_filename(filename)

            file_path = os.path.join(resource_folder, filename)
            r.raise_for_status()

            with open(file_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            # Keep track of zip files
            if zipfile.is_zipfile(file_path):
                zip_path = file_path
    
            return f"✅ {os.path.basename(file_path)}", zip_path

    except Exception as e:
        error_msg = f"❌ Error with file in folder {resource_folder}\n Error downloading at url: {url}\n --{e}\n"
        # Write to thread-local error file
        thread_error_file = f"errors_thread_{thread_id}.log"
        with open(thread_error_file, "a", encoding="utf-8") as ef:
            ef.write(error_msg + "\n")
        return error_msg, None