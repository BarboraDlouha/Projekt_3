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
    Extracts general information. (voters, envelopes, valid votes, and municipality name) 
    """
    municipality_name = "N/A"
    municipality_header = soup.find("h3", text=lambda t: "Obec" in t)
    if municipality_header:
        municipality_name = municipality_header.text.replace("Obec: ", "").strip()

    table = soup.find("table", {"id": "ps311_t1"})
    if not table:
        print("❌ No general info table found.")
        return {}

    voters = table.find("td", {"headers": "sa2"})
    envelopes = table.find("td", {"headers": "sa3"})
    valid_votes = table.find("td", {"headers": "sa6"})

    return {
        "municipality_name": municipality_name,  
        "voters": voters.text.strip() if voters else "N/A",
        "envelopes": envelopes.text.strip() if envelopes else "N/A",
        "valid_votes": valid_votes.text.strip() if valid_votes else "N/A",
    }

def extract_party_votes(soup: bs) -> Dict[str, int]:
    """
    Extracts party names and their corresponding vote counts from the HTML.
   
    """
    party_votes = {}
    
    tables = soup.find_all("table", class_="table")
    
    for table in tables:
        rows = table.find_all("tr")[2:]  
        for row in rows:
            cols = row.find_all("td")
            if len(cols) >= 3:
                party_name = cols[1].text.strip() 
                votes = cols[2].text.strip().replace(",", "")  
                
                if votes.isdigit():
                    party_votes[party_name] = int(votes)
                else:
                    party_votes[party_name] = 0   

def save_to_csv(
    municipality_data: Dict,
    party_votes: Dict[str, int],
    filename: str
):
    """
    Saves municipality data and party votes into a CSV file.

    Columns:
    - kod obce
    - nazev obce
    - registrovani volici
    - vydane obalky
    - platne hlasy
    - názvy všech stran
    """
    # Získání názvů všech stran (ze slovníku party_votes)
    all_parties = sorted(party_votes.keys())

    # Hlavička CSV souboru
    header = [
        "kod obce",
        "nazev obce",
        "registrovani volici",
        "vydane obalky",
        "platne hlasy",
    ] + all_parties

    # Otevři CSV soubor a zapisuj data
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        # Zapiš hlavičku
        writer.writerow(header)

        # Připrav data do řádku
        row = [
            municipality_data.get("municipality_code", "N/A"),  # Kod obce
            municipality_data.get("municipality_name", "N/A"),  # Název obce
            municipality_data.get("voters", "N/A"),            # Registrovaní voliči
            municipality_data.get("envelopes", "N/A"),         # Vydané obálky
            municipality_data.get("valid_votes", "N/A"),       # Platné hlasy
        ]

        # Přidej počty hlasů pro jednotlivé strany
        for party in all_parties:
            row.append(party_votes.get(party, 0))  # Hlasy pro danou stranu (0, pokud nejsou)

        # Zapiš celý řádek
        writer.writerow(row)

    print(f"✅ Data byla uložena do souboru {filename}")

def parse_arguments() -> tuple:
    """
    Parses command-line arguments to get the URL and output CSV file name.
    If arguments are missing, prompts the user to re-run the script with proper inputs.
    """
    parser = argparse.ArgumentParser(
        description="Scrape data from a specified webpage and save it to a CSV file."
    )
    parser.add_argument(
        "url",  # První argument: URL
        type=str,
        help="The URL of the webpage to scrape."
    )
    parser.add_argument(
        "output",  # Druhý argument: název CSV souboru
        type=str,
        help="The name of the output CSV file (e.g., results.csv)."
    )
    
    # Zpracuj argumenty
    args = parser.parse_args()
    
    # Validace argumentů (např. kontrola platné URL by mohla být přidána zde)
    if not args.url.startswith("http"):
        print("\n[ERROR] The URL must start with 'http' or 'https'.")
        print("Usage example:")
        print("  python projekt_3.py <URL> <output_file.csv>\n")
        sys.exit(1)
    
    return args.url, args.output

def main():
    """
    Main function to scrape data from a given URL and save it to a CSV file.
    """
    # 1. Získání argumentů
    target_url, output_csv = parse_arguments()
    print(f"Scraping data from: {target_url}")
    print(f"Results will be saved in: {output_csv}")

    # 2. Načtení relativních odkazů na municipality
    links = get_relative_links(target_url)
    if not links:
        print("⚠️ No municipalities found on the given page.")
        sys.exit(1)

    print(f"Found {len(links)} municipalities. Processing data...")

    # 3. Zpracování dat pro jednotlivé municipality
    all_data = []
    for relative_link in links:
        full_url = build_full_url(BASE_URL, relative_link)
        soup = fetch_and_parse(full_url)

        # Získání obecných informací o municipality
        general_info = extract_general_info(soup)
        general_info["municipality_code"] = extract_town_code(full_url)  # Přidáme kód obce

        # Získání hlasů pro jednotlivé strany
        party_votes = extract_party_votes(soup)

        # Přidání do seznamu všech dat
        all_data.append((general_info, party_votes))

    # 4. Zápis všech dat do CSV
    print(f"Saving data to {output_csv}...")
    for municipality_data, party_votes in all_data:
        save_to_csv(municipality_data, party_votes, output_csv)

    print("✅ Data byla úspěšně zpracována a uložena.")


#==================================================================================
# Main Program
#==================================================================================

if __name__ == "__main__":
   main()