import os
import json

def load_json_files(directory):
    data = []
    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            filepath = os.path.join(directory, filename)
            with open(filepath, 'r') as file:
                file_data = json.load(file)
                data.append(file_data)
    return data

# Directory containing the JSON files
directory = 'data/raw/pubmed/'

# Load all JSON files
json_data = load_json_files(directory)

# Print the number of files loaded
print(f"Loaded {len(json_data)} JSON files.")
