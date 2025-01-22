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
URL = "https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=4&xnumnuts=3203"




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

def parse_html(html_content: str) -> bs.BeautifulSoup:
    """
    Parses the HTML content using BeautifulSoup and returns the parsed object.
    """
    return bs.BeautifulSoup(html_content, features='html.parser')

def find_all_links(soup: bs.BeautifulSoup) -> List[str]:
    """
    Finds all links with the attribute headers="t1sb1" in the parsed HTML content.
    """
    links = soup.find_all('a', href=True, headers="t1sb1")  
    return [link['href'] for link in links]  

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
    parser.add_argument("url", type=str, help="The URL of the page to scrape.")
    args = parser.parse_args()
    return args.url













# def format_link(municipality):
#   return f"https://www.volby.cz/pls/ps2017nss/ps311?xjazyk=CZ&xkraj=4&xobec={municipality}&xvyber=3203"


#def browse_municipality():
#       print(format_link(municipality))




#==================================================================================
# Main Program
#==================================================================================
if __name__ == "__main__":
    