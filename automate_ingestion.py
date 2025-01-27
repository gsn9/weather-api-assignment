import os
import requests
import logging
from pathlib import Path
from typing import List, Optional
import argparse
import sys

# Configure logging
logging.basicConfig(
    filename="scripts/upload_all_files.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Configuration
DEFAULT_API_URL = "http://localhost:8000/api/upload_file"  # Update if different
DEFAULT_DATA_DIR = Path(
    "../data/code-challenge-template/wx_data"
)  # Adjust the path as needed
ALLOWED_EXTENSIONS = {".txt"}


def get_all_files(directory: Path, allowed_extensions: set) -> List[Path]:
    """Retrieve all files with allowed extensions from the specified directory."""
    if not directory.exists():
        logging.error(f"Data directory does not exist: {directory}")
        return []
    files = [
        file
        for file in directory.iterdir()
        if file.suffix in allowed_extensions and file.is_file()
    ]
    logging.info(f"Found {len(files)} files to upload in {directory}.")
    return files


def upload_file(file_path: Path, api_url: str) -> bool:
    """Upload a single file to the API."""
    try:
        with open(file_path, "rb") as f:
            files = {"file": (file_path.name, f, "text/plain")}
            response = requests.post(api_url, files=files)

        if response.status_code == 200:
            logging.info(f"Successfully uploaded {file_path.name}: {response.json()}")
            return True
        else:
            logging.error(
                f"Failed to upload {file_path.name}: {response.status_code} - {response.text}"
            )
            return False
    except Exception as e:
        logging.error(f"Exception uploading {file_path.name}: {e}")
        return False


def main(api_url: Optional[str] = None, data_dir: Optional[str] = None):
    """Main function to upload all files."""
    api_url = api_url or DEFAULT_API_URL
    data_dir = Path(data_dir) if data_dir else DEFAULT_DATA_DIR

    logging.info("Starting upload process.")
    logging.info(f"API URL: {api_url}")
    logging.info(f"Data Directory: {data_dir}")

    files = get_all_files(data_dir, ALLOWED_EXTENSIONS)
    if not files:
        logging.warning("No files found to upload. Exiting.")
        print("No files found to upload. Check the log for details.")
        return

    success = 0
    failure = 0
    for file in files:
        print(f"Uploading {file.name}...")
        if upload_file(file, api_url):
            success += 1
        else:
            failure += 1

    logging.info(f"Upload completed: {success} succeeded, {failure} failed.")
    print(
        f"Upload completed: {success} succeeded, {failure} failed. Check 'upload_all_files.log' for details."
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Upload all weather data files to the API."
    )
    parser.add_argument(
        "--api-url",
        type=str,
        default=DEFAULT_API_URL,
        help="The API endpoint URL for uploading files (default: http://localhost:8000/api/upload_file)",
    )
    parser.add_argument(
        "--data-dir",
        type=str,
        default=str(DEFAULT_DATA_DIR),
        help="The directory containing the data files to upload (default: ../data/code-challenge-template/wx_data)",
    )

    args = parser.parse_args()
    main(api_url=args.api_url, data_dir=args.data_dir)
