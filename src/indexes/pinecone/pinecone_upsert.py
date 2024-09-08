import os
import random
import itertools
import logging
import numpy as np
import pandas as pd
from pinecone import Pinecone
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def convert_arrays_to_lists(data):
    """
    Recursively converts all numpy arrays in a dictionary to lists.
    """
    if isinstance(data, dict):
        return {key: convert_arrays_to_lists(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [convert_arrays_to_lists(item) for item in data]
    elif isinstance(data, np.ndarray):
        return data.tolist()
    return data


def flatten_dict(d, parent_key='', sep='_'):
    """
    Recursively flattens nested dictionaries.
    """
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        elif isinstance(v, list):
            for i, item in enumerate(v):
                items.extend(flatten_dict({f'{new_key}_{i}': item}).items())
        else:
            items.append((new_key, v))
    return dict(items)


def chunks(iterable, batch_size=200):
    """
    Yields chunks of data from an iterable in batches of batch_size.
    """
    it = iter(iterable)
    chunk = list(itertools.islice(it, batch_size))
    while chunk:
        yield chunk
        chunk = list(itertools.islice(it, batch_size))


def main():
    # Initialize Pinecone client
    logging.info("Initializing Pinecone client.")
    try:
        pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"), pool_threads=30)
        index = pc.Index("pubmed-test")
    except Exception as e:
        logging.error(f"Failed to initialize Pinecone client: {e}")
        

    # Load embeddings from the parquet file
    embeddings_path = "data/features/pubmed/pinecone/formated/most_cited_papers_1998/most_cited_papers_1998.parquet"
    try:
        logging.info(f"Loading embeddings from {embeddings_path}.")
        embeddings_df = pd.read_parquet(embeddings_path)
    except Exception as e:
        logging.error(f"Error loading embeddings: {e}")
        

    # Convert embeddings to dictionary format
    logging.info("Converting embeddings to dictionary format.")
    data = embeddings_df.to_dict(orient="records")[99430:]

    for record in data:
        # Convert 'values' to list and flatten 'metadata'
        try:
            record["values"] = record.get("values").tolist()
            record["metadata"] = convert_arrays_to_lists(record["metadata"])
            flattened_metadata = flatten_dict(record["metadata"])
            record["metadata"] = {k.replace('metadata_', ''): v for k, v in flattened_metadata.items()}
        except Exception as e:
            logging.error(f"Error processing record: {e}")
            continue

    # Upsert data to Pinecone asynchronously in chunks
    logging.info("Starting asynchronous upsert requests.")
    try:
        with index as idx:
            async_results = [
                idx.upsert(vectors=chunk, async_req=True)
                for chunk in chunks(data, batch_size=200)
            ]
            logging.info("Waiting for all upsert requests to complete.")
            
            # Ensure all async requests finish
            [result.get() for result in async_results]
            logging.info("All upsert requests completed successfully.")
    except Exception as e:
        logging.error(f"Error during upsert: {e}")


if __name__ == "__main__":
    main()
