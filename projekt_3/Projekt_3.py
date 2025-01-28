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

def extract_town_code(link: str) -> str:
    """
    Extracts the town code from the URL.
    """
    if "obec=" in link:
        return link.split("obec=")[1].split("&")[0] 
    return "N/A"

def scrape_town_data(link: str, base_url: str) -> Dict:
    """
    Extracts data for a single town from the given link.
    """
    full_url = f"{base_url}/{link.lstrip('/')}"  # Sestavíme plnou URL
    html_content = load_page_source_code(full_url)  # Načteme HTML obsah stránky
    soup = parse_html(html_content)  # Parsujeme HTML pomocí BeautifulSoup

    # Název obce
    town_name = soup.find("h3").text.strip() if soup.find("h3") else "N/A"

    # Najdeme tabulku s obecnými daty
    table = soup.find("table", {"id": "ps311_t1"})
    if not table:
        print(f"❌ No table found for URL: {full_url}")
        return {}

    # Najdeme první řádek obsahující data
    row = table.find("tr", headers=True)  # Hledáme řádek, který má atribut headers
    if not row:
        print(f"❌ No data rows found in table for {full_url}")
        return {}

    # Najdeme všechny buňky v řádku
    stats = row.find_all("td")

    # Extrahujeme hodnoty na základě `headers`
    voters = table.find("td", {"headers": "sa2"})
    envelopes = table.find("td", {"headers": "sa3"})
    valid_votes = table.find("td", {"headers": "sa6"})

    # Převedeme hodnoty na text, pokud existují
    voters = voters.text.strip() if voters else "N/A"
    envelopes = envelopes.text.strip() if envelopes else "N/A"
    valid_votes = valid_votes.text.strip() if valid_votes else "N/A"

    # Hlasy pro jednotlivé strany
    parties = {}
    table_parties = soup.find("table", {"id": "ps311_t2"})
    if table_parties:
        for row in table_parties.find_all("tr")[2:]:  # Přeskakujeme hlavičku
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

def parse_arguments() -> tuple:
    """
    Parses command-line arguments to get the URL and output CSV file name.
    Both arguments are required. If not provided, the script prompts the user to enter them correctly.
    """
    parser = argparse.ArgumentParser(
        description="Scrape data from a specified webpage and save it to a CSV file."
    )
    
    parser.add_argument(
        "url",
        type=str,
        help="The URL of the page to scrape."
    )
    
    parser.add_argument(
        "--output", "-o",
        required=True,  # Povinný argument
        type=str,
        help="The name of the output CSV file."
    )

    args = parser.parse_args()

    # Ověření, zda byly zadány oba argumenty
    if not args.url or not args.output:
        print("\n❌ [ERROR] Missing required arguments!")
        print("Please provide both the URL and the output CSV file name.")
        print("\nUsage example:")
        print("  python projekt_3.py <URL> --output <output_file.csv>\n")
        sys.exit(1)  # Ukončí program

    return args.url, args.output

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