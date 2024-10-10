def extract_authors(flat_dict):
    # Initialize an empty list to store the authors
    authors = []
    index = 0
    
    while True:
        # Build the keys for ForeName, LastName, and Initials
        fore_name_key = f'abstract_authors_list_Author_ForeName_{index}'
        last_name_key = f'abstract_authors_list_Author_LastName_{index}'
        initials_key = f'abstract_authors_list_Author_Initials_{index}'
        collective_name_key = f'abstract_authors_list_Author_CollectiveName_{index}'
        
        # Check if at least one name key exists, otherwise break the loop
        if fore_name_key not in flat_dict and last_name_key not in flat_dict and collective_name_key not in flat_dict:
            break
        
        # Handle CollectiveName if available
        if collective_name_key in flat_dict and flat_dict[collective_name_key]:
            authors.append(flat_dict[collective_name_key])
        else:
            # Extract ForeName, LastName, and Initials
            fore_name = flat_dict.get(fore_name_key, "")
            last_name = flat_dict.get(last_name_key, "")
            initials = flat_dict.get(initials_key, "")
            
            # Construct the full author name
            if fore_name or last_name:
                author_name = f"{fore_name} {initials} {last_name}".strip()
                authors.append(author_name)
        
        # Increment index to process the next author
        index += 1

    return authors

def consolidate_author_keys(flat_dict):
    # Extract authors using the previous function
    authors_list = extract_authors(flat_dict)
    
    # Remove all keys related to abstract_authors_list_Author_*
    keys_to_remove = [key for key in flat_dict if key.startswith('abstract_authors_list_Author_')]
    
    for key in keys_to_remove:
        del flat_dict[key]
    
    # Add the consolidated author list to the dictionary
    flat_dict['authors'] = authors_list
    
    return flat_dict

def consolidate_dates(flat_dict):
    # Extract date and date_revised fields
    consolidated_date = {
        'Day': flat_dict.pop('date_Day', None),
        'Month': flat_dict.pop('date_Month', None),
        'Year': flat_dict.pop('date_Year', None)
    }

    consolidated_revised_date = {
        'Day': flat_dict.pop('date_revised_Day', None),
        'Month': flat_dict.pop('date_revised_Month', None),
        'Year': flat_dict.pop('date_revised_Year', None)
    }

    # Add the consolidated date fields back to the dictionarBy
    flat_dict['date'] = consolidated_date
    flat_dict['date_revised'] = consolidated_revised_date
    
    return flat_dict

def consolidate_flat_dict(flat_dict):
    flat_dict = consolidate_author_keys(flat_dict)
    flat_dict = consolidate_dates(flat_dict)
    return flat_dict

