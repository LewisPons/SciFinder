import json
import math
import random
import logging
import time
from pathlib import Path
from typing import Dict, List, Optional

import polars as pl

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def load_json(file_path: Path) -> Dict:
    """
    Load a JSON file and return its content.
    """
    try:
        return json.loads(file_path.read_text())
    except FileNotFoundError:
        logging.error(f"The file at {file_path} was not found.")
    except json.JSONDecodeError:
        logging.error(f"The file at {file_path} is not a valid JSON file.")
    return {}


def list_json_files(directory: Path, sample_proportion: Optional[float] = None) -> List[Path]:
    """
    List JSON files in the given directory, optionally returning a random sample.
    """
    json_files = list(directory.glob('*.json'))

    if sample_proportion is not None:
        if not 0 < sample_proportion <= 1:
            raise ValueError("sample_proportion must be between 0 and 1")
        sample_size = math.ceil(len(json_files) * sample_proportion)
        return random.sample(json_files, sample_size)

    return json_files


def convert_to_parquet_and_partition(data: List[Dict], output_dir: Path) -> None:
    """
    Convert the data to a Polars DataFrame, partition it by year and language, and save it as Parquet files.
    """
    df = pl.DataFrame(data)
    df.write_parquet(
        output_dir,
        use_pyarrow=True,
        pyarrow_options={"partition_cols": ["year", "language"]},
    )


def load_and_process_pubmed_json_files(file_paths: List[Path], output_directory: Path) -> None:
    """
    Load specified JSON files, validate their structure, and convert them to partitioned Parquet files.B
    """
    for file_path in file_paths:
        file_name = file_path.name
        file_data = load_json(file_path)

        if not file_data:
            logging.warning(f"Skipping empty or invalid file: {file_name}")
            continue

        try:
            convert_to_parquet_and_partition(file_data, output_directory)
            logging.info(f"'{file_name}' has been converted to Parquet and partitioned by year and language.")
        except Exception as e:
            logging.error(f"Error processing {file_name}: {str(e)}")


def main():
    start_time = time.time()
    raw_files_dir = Path("data/raw/pubmed/")
    output_dir = Path("data/processed/pubmed")

    raw_files_paths = list_json_files(raw_files_dir)
    if not raw_files_paths:
        logging.error("No JSON files found in the specified directory.")
        return
    
    load_and_process_pubmed_json_files(raw_files_paths, output_dir)
    elapsed_time = time.time() - start_time
    logging.info(f"Total processing time: {elapsed_time:.2f} seconds.")


if __name__ == "__main__":
    main()
