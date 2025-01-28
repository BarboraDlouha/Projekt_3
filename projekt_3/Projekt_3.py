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
import requests
import argparse
from typing import List
from bs4 import BeautifulSoup as bs


#==================================================================================
# Global variables and constants
#==================================================================================
DEFAULT_URL = "https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=4&xnumnuts=3203"
BASE_URL = "https://www.volby.cz"

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

def find_all_links(soup: bs) -> List[str]:
    """
    Finds all <a> links within <td> elements with specific headers using CSS selectors.
    """
    header_values = ["t1sa1 t1sb1", "t2sa1 t2sb1", "t3sa1 t3sb1", "t4sa1 t4sb1"]
    links = []

    for header in header_values:
        found_links = soup.select(f'td[headers="{header}"] a[href]') 
        links.extend([link['href'] for link in found_links])  
    
    return links 

def get_links(url: str) -> List[str]:
    """
    Fetches the HTML content of the page, parses it, and finds all matching links.
    """
    html_content = load_page_source_code(url)
    soup = parse_html(html_content)
    return find_all_links(soup)

def extract_town_code(link: str) -> str:
    """
    Extracts the town code from the URL.
    """
    if "obec=" in link:
        return link.split("obec=")[1].split("&")[0] 
    return "N/A"
    
def parse_arguments() -> str:
    """
    Parses command-line arguments to get the URL.
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

def scrape_town_data(link: str, base_url: str) -> Dict:
    """
    Extracts data for a single town from the given link.
    """
    full_url = f"{base_url}/{link}"  # Sestavíme plnou URL
    html_content = load_page_source_code(full_url)  # Načteme HTML obsah stránky
    soup = parse_html(html_content)  # Parsujeme HTML obsah pomocí BeautifulSoup

    # Název obce
    town_name = soup.find("h3").text.strip() if soup.find("h3") else "N/A"

    # Tabulka s daty
    table = soup.find("table", {"id": "ps311_t1"})
    if not table:
        return {}

    rows = table.find_all("tr")

    # Hodnoty: voliči, obálky, platné hlasy
    voters, envelopes, valid_votes = "N/A", "N/A", "N/A"
    if len(rows) >= 2:
        stats = rows[1].find_all("td")
        voters = stats[3].text.strip()
        envelopes = stats[4].text.strip()
        valid_votes = stats[7].text.strip()

    # Hlasy pro jednotlivé strany
    parties = {}
    table_parties = soup.find("table", {"id": "ps311_t2"})
    if table_parties:
        for row in table_parties.find_all("tr")[2:]:
            cols = row.find_all("td")
            if len(cols) >= 2:
                party_name = cols[1].text.strip()
                votes = cols[2].text.strip()
                parties[party_name] = votes

    return {
        "town_code": extract_town_code(link),
        "town_name": town_name,
        "voters": voters,
        "envelopes": envelopes,
        "valid_votes": valid_votes,
        "parties": parties,
    }
def save_to_csv(data: List[Dict], filename: str):
    """
    Saves the collected data into a CSV file with party names as columns.
    """
    # Získání všech unikátních názvů stran
    all_parties = set()
    for entry in data:
        all_parties.update(entry["parties"].keys())
    all_parties = sorted(all_parties)  # Setřídění názvů stran

    # Hlavička CSV souboru
    header = ["Kód obce", "Název obce", "Voliči v seznamu", "Vydané obálky", "Platné hlasy"] + all_parties

    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        # Zápis hlavičky
        writer.writerow(header)

        # Zápis dat
        for entry in data:
            # Základní údaje o obci
            row = [
                entry["town_code"],
                entry["town_name"],
                entry["voters"],
                entry["envelopes"],
                entry["valid_votes"],
            ]
            # Přidání počtu hlasů pro každou stranu
            for party in all_parties:
                row.append(entry["parties"].get(party, "0"))  # Pokud strana nemá hlasy, zapíšeme "0"
            
            writer.writerow(row)

    print(f"Data byla uložena do souboru {filename}")

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