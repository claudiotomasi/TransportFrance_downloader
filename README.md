# TransportFrance Downloader

A Python tool to download public transit datasets from [Transport.data.gouv.fr](https://transport.data.gouv.fr/) with optional ZIP extraction. The script can download multiple datasets in parallel, organize them in folders by dataset and format, and handle ZIP extraction if requested.

---

## Features

- Download datasets from `transport.data.gouv.fr`
- Supports multiple dataset formats (`zip`, `GTFS`, `NeTEx`, `csv`, `json`, and more)
- Optional ZIP extraction into structured subfolders
- Parallel downloading with configurable number of threads
- Error logging for failed downloads or extractions
- Automatically sanitizes filenames for safe storage

---

## Installation

1. Clone this repository:

```bash
git clone https://github.com/YOUR_USERNAME/TransportFrance_downloader.git
cd TransportFrance_downloader
```

2. Create a virtual environment (optional but recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

---

## Usage

Run the main script:

```bash
python main.py [OPTIONS]
```

### Arguments

| Option | Description |
|--------|-------------|
| `-zip`, `--extract-zip` | Extract ZIP files after download. |
| `-t`, `--max-threads INT` | Maximum number of parallel download threads. If not set, the tool automatically chooses based on CPU cores. |
| `-o`, `--output-directory DIR` | Directory where downloaded files will be saved. Default: `./downloads` |


### Examples

1. **Download datasets without extracting ZIP files**:

```bash
python main.py
```

2. **Download datasets and extract ZIP files**:

```bash
python main.py --extract-zip
```

3. **Download datasets with a custom output directory:**

```bash
python main.py --output-directory /path/to/save
```

4. **Download datasets using a specific number of threads:**

```bash
python main.py --max-threads 8
```

### Output Structure

Downloaded files are organized as:

```
output_directory/
├── Dataset_Title/
│   ├── Format/
│   │   ├── Resource_Title_YYYY-MM-DD/
│   │   │   ├── file1.zip
│   │   │   └── file2.csv
```

If -zip is used, ZIP files will be extracted into a folder with the same name as the ZIP:
```bash
file1.zip -> file1/
```

## Error Logs

- Download errors are logged into `errors.log` in the output directory.
- ZIP extraction errors are logged into `extraction_errors.log`.

---

## Dependencies

- Python 3.10+
- `requests`
- `pandas`
- `tqdm`
- `colorama`

All dependencies can be installed via:
```bash
pip install -r requirements.txt






