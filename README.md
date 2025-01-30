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

Program se spouští z terminálu a vyžaduje dva parametry:

1. **URL** s volebními daty
2. **Název výstupního CSV souboru**

Příkaz pro spuštění:

```bash
python projekt_3.py "https://www.volby.cz/pls/ps2017nss/..." --output vysledky.csv
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

## 🛠 Možné problémy a jejich řešení

| Problém                                     | Řešení                                                                             |
| ------------------------------------------- | ---------------------------------------------------------------------------------- |
| Program nevygeneroval žádná data            | Ověřte, že jste zadali správné URL s volebními daty.                               |
| CSV se nezobrazuje správně v Excelu         | Použijte UTF-8-SIG, který je už v projektu nastaven.                               |
| Chyba `IndexError: list index out of range` | Struktura tabulky se mohla změnit, ujistěte se, že selektory odpovídají HTML kódu. |

---

## 📩 Kontakt

**Autor:** Barbora Dlouhá**Email:** [Barbora-Dlouha@seznam.cz](mailto\:Barbora-Dlouha@seznam.cz)
