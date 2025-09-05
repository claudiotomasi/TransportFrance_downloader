import re
import os
import urllib.parse

def get_max_workers():
    cpu_count = os.cpu_count() or 1  # fallback to 1 if undetectable
    # For I/O-bound tasks like downloads, a factor of 5-10x CPU cores is reasonable
    return min(32, cpu_count * 5)  # max 32 threads to avoid too many connections
    
def sanitize_filename(filename):
    # Replace any character not allowed in filenames with underscore
    return re.sub(r'[\/:*?"<>|]', '_', filename)
    
def get_filename_from_cd(cd):
    """
    Extract filename from Content-Disposition header.
    Supports both filename= and filename*= cases.
    """
    if not cd:
        return None

    # Check for RFC 5987 format: filename*=UTF-8''encoded.zip
    fname_star = re.findall(r"filename\*\s*=\s*([^']+)''(.+)", cd)
    if fname_star:
        encoding, filename = fname_star[0]
        return urllib.parse.unquote(filename, encoding=encoding)

    # Fallback: filename="file.zip" or filename=file.zip
    fname = re.findall(r'filename="?([^";]+)"?', cd)
    if fname:
        return fname[0]

    return None
