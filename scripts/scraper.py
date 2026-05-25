import urllib.request
from bs4 import BeautifulSoup
import json

def scrape_python_errors():
    print("Connecting to python.org...")
    url = "https://docs.python.org/3/library/exceptions.html"
    
    # Download the webpage
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response:
        html = response.read().decode('utf-8')
    
    # Parse the raw HTML into a searchable object
    soup = BeautifulSoup(html, 'html.parser')
    
    scraped_data = []
    
    # Python's docs wrap every exception in a <dl class="exception"> tag
    for exception_block in soup.find_all('dl', class_='exception'):
        
        # The actual name of the error is in the <dt> tag's ID attribute
        dt_tag = exception_block.find('dt')
        if not dt_tag:
            continue
            
        # Clean up the ID to get just the error name (e.g., "exceptions.ValueError" -> "ValueError")
        raw_id = dt_tag.get('id', '')
        error_name = raw_id.split('.')[-1]
        
        # The official description is in the <dd> tag right below it
        dd_tag = exception_block.find('dd')
        
        # Grab the first sentence of the description
        description = dd_tag.text.strip().split('\n')[0] if dd_tag else "No description available."
        
        # We only want actual Errors, not base warning classes
        if "Error" in error_name:
            scraped_data.append({
                "error_name": error_name,
                "official_description": description,
                "needs_regex": True # Flag to tell us we still need to write a pattern for this!
            })
            
    print(f"Found {len(scraped_data)} built-in Python errors!")
    
    # Save our massive new dataset to a JSON file
    output_file = 'scraped_errors_database.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(scraped_data, f, indent=4)
        
    print(f"Data successfully saved to {output_file}")

if __name__ == "__main__":
    scrape_python_errors()