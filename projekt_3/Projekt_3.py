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
import csv
import sys
import argparse
import requests
from typing import List, Dict
from urllib.parse import urljoin
from bs4 import BeautifulSoup as bs
print(sys.argv)

#==================================================================================
# Global variables and constants
#==================================================================================
DEFAULT_URL = "https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=4&xnumnuts=3203"
BASE_URL = "https://www.volby.cz/pls/ps2017nss/"

#==================================================================================
# Function definitions:
#==================================================================================
def load_page_source_code(url: str) -> str:
    """
    Sends a GET request to the page and returns its HTML content if successful.
    Returns None if the request fails.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()  
    except requests.RequestException as e:
        print(f"Error fetching the page: {e}")
        sys.exit(1)   
    else:
        return response.text

def parse_html(html_content: str) -> bs:
    """
    Parses the HTML content using BeautifulSoup and returns the parsed object.
    """
    return bs(html_content, features='html.parser')

def fetch_and_parse(url: str) -> bs:
    """
    Combines `load_page_source_code` and `parse_html` to fetch and parse a webpage.
    Returns the parsed BeautifulSoup object.
    """
    html_content = load_page_source_code(url)  
    return parse_html(html_content)

def find_relative_links(soup: bs) -> List[str]:
    """
    Finds relative links for individual administrative units."
    """
    header_values = ["t1sa1 t1sb1", "t2sa1 t2sb1", "t3sa1 t3sb1", "t4sa1 t4sb1"]
    links = []

    for header in header_values:
        found_links = soup.select(f'td[headers="{header}"] a[href]') 
        links.extend([link['href'] for link in found_links])  
    
    return links 

def get_relative_links(url: str) -> List[str]:
    """
    Fetches the HTML content of the page, parses it, and finds all matching links.
    """
    soup = fetch_and_parse(url)
    return find_relative_links(soup)

def build_full_url(base_url: str, relative_link: str) -> str:
    """
    Combines the base URL with a relative link to create a full URL.
    """
    return urljoin(base_url, relative_link)

def extract_town_code(full_url: str) -> str:
    """
    Extracts the town code from a full URL.
    """
    if "obec=" in full_url:
        return full_url.split("obec=")[1].split("&")[0]
    return "N/A"

def extract_general_info(soup: bs) -> Dict:
    """
    Extracts general information (voters, envelopes, valid votes, and town name) 
    from the `ps311_t1` table and related elements.
    """
    # Název územního celku (např. obce)
    town_name = "N/A"
    town_header = soup.find("h3", text=lambda t: "Obec" in t)
    if town_header:
        town_name = town_header.text.replace("Obec: ", "").strip()

    # Tabulka s obecnými daty
    table = soup.find("table", {"id": "ps311_t1"})
    if not table:
        print("❌ No general info table found.")
        return {}

    # Extrakce počtů voličů, obálek a platných hlasů
    voters = table.find("td", {"headers": "sa2"})
    envelopes = table.find("td", {"headers": "sa3"})
    valid_votes = table.find("td", {"headers": "sa6"})

    return {
        "town_name": town_name,  # Přidán název obce
        "voters": voters.text.strip() if voters else "N/A",
        "envelopes": envelopes.text.strip() if envelopes else "N/A",
        "valid_votes": valid_votes.text.strip() if valid_votes else "N/A",
    }


#==================================================================================
# Main Program
#==================================================================================

if __name__ == "__main__":
    target_url, output_csv = parse_arguments()

    print(f"Scraping links from: {target_url}")
    links = get_links(target_url)

    if links:
        print(f"Found {len(links)} links. Scraping data...")
        scraped_data = []

        # Scrapování dat z jednotlivých odkazů
        for link in links:
            full_link = f"{BASE_URL}/{link}"  # Sestavení úplné URL
            print(f"Processing: {full_link}")

            town_data = scrape_town_data(link, BASE_URL)
            if town_data:
                scraped_data.append(town_data)

        # Uložit data do CSV pouze pokud něco bylo nalezeno
        if scraped_data:
            print(f"Saving {len(scraped_data)} records to {output_csv}...")
            save_to_csv(scraped_data, output_csv)
            print(f"✅ CSV file '{output_csv}' successfully saved.")
        else:
            print("⚠️ No data extracted from the links.")
    else:
        print("⚠️ No matching links found.")