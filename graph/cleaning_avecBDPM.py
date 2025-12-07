import csv
import re
import unicodedata

# ----------------------
# Normalisation des noms
# ----------------------
def normalize_name(name):
    """
    Normalise un nom de médicament : supprime accents, met en majuscules, remplace ponctuation par espace
    """
    name = unicodedata.normalize('NFKD', name).encode('ASCII', 'ignore').decode('utf-8')
    name = name.upper()
    name = re.sub(r'[^\w\s]', ' ', name)
    name = re.sub(r'\s+', ' ', name).strip()
    return name

# ----------------------
# Charger BDPM et construire dictionnaire nom → code CIS
# ----------------------
def load_bdpm(file_path="data/raw/CIS_bdpm.txt"):
    bdpm_dict = {}
    with open(file_path, encoding="latin1") as f:
        for line in f:
            parts = line.strip().split("\t")
            if len(parts) > 1:
                cis_code = parts[0]
                nom = normalize_name(parts[1])
                words = nom.split()
                for w in words:
                    if w not in bdpm_dict:
                        bdpm_dict[w] = cis_code
    return bdpm_dict

# ----------------------
# Extraire les interactions
# ----------------------
def extract_interactions(text, bdpm_dict):
    """
    Extrait tous les mots du texte et cherche une correspondance dans BDPM
    """
    words = re.findall(r'\b\w+\b', normalize_name(text))
    found = set()
    for w in words:
        cis = bdpm_dict.get(w)
        if cis:
            found.add(cis)
    return list(found)

# ----------------------
# Traitement principal
# ----------------------
if __name__ == "__main__":
    bdpm_dict = load_bdpm("data/raw/CIS_bdpm.txt")
    print(f"Dictionnaire BDPM chargé avec {len(bdpm_dict)} entrées.")

    cleaned_records = []

    # raw_openfda.csv : colonne 1 → drug, colonne 2 → interactions_text
    with open("data/raw/raw_openfda.csv", newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            drug_name = normalize_name(row["drug"])
            # correspondance avec BDPM sur tous les mots
            words = drug_name.split()
            cis_code = None
            for w in words:
                if w in bdpm_dict:
                    cis_code = bdpm_dict[w]
                    break
            if not cis_code:
                continue  # médicament inconnu

            # extraction interactions
            interactions = extract_interactions(row.get("interactions_text", ""), bdpm_dict)
            cleaned_records.append((cis_code, interactions))

    output_path = "data/raw/clean_openfda_bdpm.csv"
    with open(output_path, "w", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["drug_code", "interactions"])
        for cis, inter in cleaned_records:
            writer.writerow([cis, ";".join(inter)])

    print(f"CSV nettoyé '{output_path}' généré avec {len(cleaned_records)} médicaments reconnus.")
