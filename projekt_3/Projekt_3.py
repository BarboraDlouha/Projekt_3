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
from bs4 import BeautifulSoup as bs


#==================================================================================
# Global variables and constants
#==================================================================================
url = "https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=4&xnumnuts=3203"




#==================================================================================
# Function definitions:
#==================================================================================
def send_request_get(url: str) -> str:
    """
    Return the server response to a GET request.
    """
    response = requests.get(url)
    if response.status_code == 200:
        return response.text  
    else:
        print("Error loading page.")
        return None  
   


def get_parsed_response(response: str) -> bs.BeautifulSoup:
    """
    Get a split response to a GET request.
    """
    return bs.BeautifulSoup(response, features="html.parser")


def vyber_tr_tagy(odpoved_serveru: bs4.BeautifulSoup) -> bs4.element.ResultSet:
    """
    Ze zdrojového kódu stránky vyber všechny tagy "tr".
    """
    return odpoved_serveru.find_all("tr")


def rozdel_zahlavi_a_transakce(trs: bs4.element.ResultSet) -> tuple:
    """
    Vrať z tagů "tr" pouze záhlaví a informace ke všem transakcím.
    """
    zahlavi, *transakce = trs[2:]
    zahlavi: list = zahlavi.get_text().splitlines()[1:]
    return zahlavi, transakce


if __name__ == "__main__":
    url: str =  \
        "https://ib.fio.cz/ib/transparent?a=2801322199&f=01.07.2023&t=03.07.2023"
    odpoved = ziskej_parsovanou_odpoved(posli_pozadavek_get(url))
    zahlavi, transakce = rozdel_zahlavi_a_transakce(vyber_tr_tagy(odpoved))
    print(transakce)









def format_link(municipality):
    return f"https://www.volby.cz/pls/ps2017nss/ps311?xjazyk=CZ&xkraj=4&xobec={municipality}&xvyber=3203"


def browse_municipality():
    for municipality in range(2017, 2022):
        print(formatting_link(municipality))




#==================================================================================
# Main Program
#==================================================================================
if __name__ == "__main__":
    browse_municipality()