from datasets import load_dataset
from os import path, makedirs
from typing import Dict, List, Optional
from tqdm import tqdm
import json
import logging

# Define constants
TARGET_PATH = 'data/raw/pubmed'
PORTION_SIZE = 10000  # 10k entries per portion
LOG_INTERVAL = 1000   # Logging progress every 1000 entries

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def setup_directory() -> None:
    """Create target directory if it doesn't exist."""
    makedirs(TARGET_PATH, exist_ok=True)

def save_portion(portion: List[Dict], counter: int) -> None:
    """Saves a portion of PubMed data to a JSON file."""
    filename = path.join(TARGET_PATH, f'pubmed_portion_{counter}.json')
    with open(filename, 'w') as fp:
        json.dump(portion, fp, indent=2)
    logger.info(f"Saved portion {counter} with {len(portion)} entries to {filename}")

def process_entry(entry: Dict) -> Optional[Dict]:
    """Processes a single PubMed entry and extracts relevant fields."""
    try:
        medline_citation = entry['MedlineCitation']
        article = medline_citation['Article']
        abstract = article.get('Abstract', {})
        
        abstract_text = abstract.get('AbstractText', '')
        abstract_title = article.get('ArticleTitle', '')
        abstract_authors_list = article.get('AuthorList', [])

        # Check that the abstract text, title, or authors are not empty
        if len(abstract_text) > 20 and len(abstract_title) > 5 and len(abstract_authors_list) > 0:
            return {
                'pmid': medline_citation['PMID'],
                'year': medline_citation['DateCompleted']['Year'],
                'date': medline_citation['DateCompleted'],
                'number_of_referenced': medline_citation.get('NumberOfReferences'),
                'date_revised': medline_citation.get('DateRevised'),
                'language': article.get('Language'),
                'abstract_text': abstract_text,
                'abstract_title': abstract_title,
                'abstract_authors_list': abstract_authors_list,
                'medline_journal_info': medline_citation.get('MedlineJournalInfo'),
                'pubmed_data': entry.get('PubmedData')
            }
    except KeyError as e:
        logger.warning(f"Key error: {e} in entry with PMID {entry.get('MedlineCitation', {}).get('PMID')}")
    except Exception as e:
        logger.error(f"Unexpected error: {e} in entry with PMID {entry.get('MedlineCitation', {}).get('PMID')}")
    return None

def main() -> None:
    logger.info("Starting PubMed Extraction...")
    setup_directory()

    # Load the PubMed dataset in streaming mode
    full_pubmed = load_dataset('pubmed', streaming=True)

    pubmed_portion = []
    counter = 0

    for idx, entry in tqdm(enumerate(full_pubmed['train']), desc="Processing entries", position=0):
        processed_entry = process_entry(entry)
        if processed_entry:
            pubmed_portion.append(processed_entry)

        if idx % LOG_INTERVAL == 0 and idx != 0:
            logger.info(f"Processed {idx} entries")

        if len(pubmed_portion) >= PORTION_SIZE:
            save_portion(pubmed_portion, counter)
            pubmed_portion = []
            counter += 1

    # Save any remaining entries after the loop ends
    if pubmed_portion:
        save_portion(pubmed_portion, counter)

    logger.info("PubMed Extraction Completed.")

if __name__ == "__main__":
    main()
