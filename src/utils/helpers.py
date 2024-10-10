
from datetime import datetime

def parse_date(date_dict):
    # Extract and convert dictionary values to integers
    day = int(date_dict.get('Day', 1))    # Default to 1 if key is missing
    month = int(date_dict.get('Month', 1)) # Default to 1 if key is missing
    year = int(date_dict.get('Year', 1900)) # Default to 1900 if key is missing

    # Create a datetime object
    parsed_date = datetime(year, month, day)

    # Format the date into a human-readable string
    return parsed_date.strftime("%d %B %Y")

# Example usage
date_dict = {'Day': 10.0, 'Month': 9.0, 'Year': 2010.0}
print(parse_date(date_dict))  # Output: "10 September 2010"
