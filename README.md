# Projekt 3 - Analýza volebních výsledků

Tento projekt slouží k automatickému stahování a analýze volebních výsledků z webu **volby.cz**. Program extrahuje data o voličích, vydaných obálkách, platných hlasech a rozložení hlasů mezi politické strany pro jednotlivé obce a ukládá je do CSV souboru.

---

## 📌 Požadavky

- **Python 3.10+**
- Instalace knihoven:
  ```bash
  pip install -r requirements.txt
  ```
  
---

## 🚀 Jak spustit

1️⃣ **Naklonuj projekt z GitHubu**  
```bash
git clone https://github.com/tvoje-jmeno/projekt_3.git
cd projekt_3
```

2️⃣ **Nainstaluj požadované knihovny**  
```bash
pip install -r requirements.txt
```

3️⃣ **Spusť skript s argumenty**  

- **URL s volebními daty** (např. `https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=4&xnumnuts=3203`)
- **Název výstupního CSV souboru** (např. `results_Pilsen_city.csv`)

```bash
python projekt_3.py "https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=4&xnumnuts=3203" results_Pilsen_city.csv
```

---

## 📊 Ukázka výstupu

Program vygeneruje soubor **CSV**, který obsahuje tabulková data. Strany jsou uloženy jako jednotlivé sloupce.

| Town Code | Town Name | Registered Voters | Envelopes Issued | Valid Votes | Party A | Party B | Party C |
| --------- | --------- | ----------------- | ---------------- | ----------- | ------- | ------- | ------- |
| 12345     | Prague    | 1000              | 800              | 780         | 400     | 300     | 80      |
| 12346     | Brno      | 500               | 450              | 440         | 200     | 150     | 90      |

**CSV je uloženo v kódování UTF-8-SIG** pro správné zobrazení v Excelu.

---

## 👮️‍♂️ Autor

**Autor:** Barbora Dlouhá  
**Email:** [Barbora-Dlouha@seznam.cz](mailto\:Barbora-Dlouha@seznam.cz)



