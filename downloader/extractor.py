import os
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

def extract_zip_file(zf, output_folder, thread_id):
    """Extract a single zip file, return error if any."""
    folder = os.path.join(os.path.dirname(zf), os.path.splitext(os.path.basename(zf))[0])
    os.makedirs(folder, exist_ok=True)

    try:
        with zipfile.ZipFile(zf, "r") as zip_ref:
            zip_ref.extractall(folder)
        return f"✅ Extracted {os.path.basename(zf)}", None
    except Exception as e:
        error_msg = f"❌ Failed to extract {zf}\n --{e}\n"
        # Thread-local error log
        thread_error_file = os.path.join(output_folder, f"extraction_errors_thread_{thread_id}.log")
        with open(thread_error_file, "a", encoding="utf-8") as logf:
            logf.write(error_msg + "\n")
        return None, error_msg


	