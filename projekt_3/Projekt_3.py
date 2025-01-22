#==================================================================================
# Header
#==================================================================================

print(60 * "-")
print("""
projekt_3.py: třetí projekt do Engeto Online Python Akademie

author: Barbora Dlouha
email: Barbora-Dlouha@seznam.cz
""")
print(60 * "-")

#==================================================================================
# Import libraries and modules
#==================================================================================
import requests
import argparse
from typing import Optional, List
from bs4 import BeautifulSoup as bs


#==================================================================================
# Global variables and constants
#==================================================================================
DEFAULT_URL = "https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=4&xnumnuts=3203"

#==================================================================================
# Function definitions:
#==================================================================================
def load_page_source_code(url: str) -> Optional[str]:
    """
    Sends a GET request to the page and returns its HTML content if successful.
    Returns None if the request fails.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()  
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching the page: {e}")
        return None 

def parse_html(html_content: str) -> bs:
    """
    Parses the HTML content using BeautifulSoup and returns the parsed object.
    """
    return bs(html_content, features='html.parser')

def find_all_links(soup: bs) -> List[str]:
    """
    Finds all <a> links within <td> elements with specific headers using CSS selectors.
    """
    header_values = ["t1sa1 t1sb1", "t2sa1 t2sb1", "t3sa1 t3sb1"]
    links = []

    for header in header_values:
        found_links = soup.select(f'td[headers="{header}"] a[href]') 
        links.extend([link['href'] for link in found_links])  
    
    return links 

def get_links(url: str) -> List[str]:
    """
    Fetches the HTML content of the page, parses it, and finds all matching links.
    """
    try:
        html_content = load_page_source_code(url)
        if not html_content:
            raise ValueError("No content fetched from the provided URL.")
    except Exception as e:
        print(f"Error in get_links: {e}")
        return []
    else:
        soup = parse_html(html_content)
        return find_all_links(soup)
    
def parse_arguments() -> str:
    """
    Parses command-line arguments to get the URL.

    Returns:
    - str: The URL provided as a command-line argument.
    """
    parser = argparse.ArgumentParser(description="Scrape links from a specified webpage.")
    parser.add_argument(
        "url",
        nargs="?",  
        default=DEFAULT_URL,  
        type=str,
        help="The URL of the page to scrape (default is the predefined URL)."
    )
    args = parser.parse_args()
    return args.url


#==================================================================================
# Main Program
#==================================================================================
if __name__ == "__main__":
    target_url = parse_arguments()

    print(f"Scraping links from: {target_url}")
    links = get_links(target_url)

    if links:
        print(f"Found {len(links)} links:")
        for link in links:
            print(link)
    else:
        print("No matching links found.")