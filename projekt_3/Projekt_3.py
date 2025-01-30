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

#==================================================================================
# Global variables and constants
#==================================================================================
BASE_URL = "https://www.volby.cz/pls/ps2017nss/"

#==================================================================================
# Function definitions:
#==================================================================================
def parse_arguments() -> tuple:
    """
    Parses command-line arguments, checks if the URL is reachable.
    """
    parser = argparse.ArgumentParser(
        description="Scrape data from a specified webpage and save it to a CSV file."
    )
    parser.add_argument("url", type=str, help="The URL of the webpage to scrape.")
    parser.add_argument("output", type=str, help="The name of the output CSV file.")

    args = parser.parse_args()

    try:
        response = requests.get(args.url, timeout=5)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"\n[ERROR] Cannot access the URL: {e}")
        sys.exit(1) 
    return args.url, args.output

def load_page_source_code(url: str) -> str:
    """
    Sends a GET request to the page and returns its HTML content if successful.
    Returns None if the request fails.
    """
    response = requests.get(url)
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
    municipality_header = soup.find("h3", string=lambda t: "Obec" in t)
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
    return party_votes

def process_municipality(relative_link: str) -> tuple:
    """
    Processes a single municipality: builds the full URL, fetches data, extracts general info
    and party votes, and returns them in a structured format.
    """
    full_url = build_full_url(BASE_URL, relative_link)
    soup = fetch_and_parse(full_url)

    general_info = extract_general_info(soup)

    if not general_info:
        print(f"⚠️ No data found for {relative_link}. Skipping...")
        return None

    general_info["municipality_code"] = extract_town_code(full_url)

    party_votes = extract_party_votes(soup)

    return general_info, party_votes

def save_to_csv(all_data: List[Dict], filename: str):
    """
    Saves the scraped election data into a CSV file.
    
    Columns:
    - municipality code
    - municipality name
    - registered voters
    - issued envelopes
    - valid votes
    - individual parties as columns (each party will have its own column)
    """
    all_parties = set()
    for municipality_data, party_votes in all_data:
        all_parties.update(party_votes.keys())

    all_parties = sorted(all_parties)

    header = [
        "municipality code",
        "municipality name",
        "registered voters",
        "issued envelopes",
        "valid votes",
    ] + all_parties

    with open(filename, mode="w", newline="", encoding="utf-8-sig") as file:
        writer = csv.writer(file, delimiter=";")

        writer.writerow(header)

        for municipality_data, party_votes in all_data:
            row = [
                municipality_data.get("municipality_code", "N/A"),
                municipality_data.get("municipality_name", "N/A"),
                int(str(municipality_data.get("voters", "0").replace(" ", "").replace("\xa0", ""))),  
                int(str(municipality_data.get("envelopes", "0").replace(" ", "").replace("\xa0", ""))),  
                int(str(municipality_data.get("valid_votes", "0").replace(" ", "").replace("\xa0", ""))),  
            ]

            for party in all_parties:
                row.append(int(str(party_votes.get(party, "0")).replace(" ", "").replace("\xa0", "")))

            writer.writerow(row)

    print(f"✅ Data byla uložena do souboru {filename}")

    

def main():
    """
    Main function to scrape data from a given URL and save it to a CSV file.
    """
    # Getting the required arguments from the user
    target_url, output_csv = parse_arguments()
    print(f"Scraping data from: {target_url}")
    print(f"Results will be saved in: {output_csv}")

    # Loading links to municipalities
    links = get_relative_links(target_url)
    if not links:
        print("⚠️ No municipalities found on the given page.")
        sys.exit(1)

    print(f"Found {len(links)} municipalities. Processing data...")

    # Data processing for all municipalities
    all_data = [process_municipality(link) for link in links if process_municipality(link)]

    # Saving data to a csv file
    print(f"Saving data to {output_csv}...")
    save_to_csv(all_data, output_csv)

    print("✅ Data byla úspěšně zpracována a uložena.")

#==================================================================================
# Main Program
#==================================================================================

if __name__ == "__main__":
   main()

   d