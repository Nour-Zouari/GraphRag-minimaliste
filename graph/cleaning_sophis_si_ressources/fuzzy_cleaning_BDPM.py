import csv
import re
import unicodedata
from fuzzywuzzy import fuzz

# ----------------------
# Normalisation des noms
# ----------------------
def normalize_name(name):
    name = unicodedata.normalize('NFKD', name).encode('ASCII', 'ignore').decode('utf-8')
    name = name.upper()
    name = re.sub(r'[^\w\s]', ' ', name)
    name = re.sub(r'\s+', ' ', name).strip()
    return name

# ----------------------
# Charger le fichier BDPM en dictionnaire nom complet → code CIS
# ----------------------
def load_bdpm(file_path="data/raw/CIS_bdpm.txt"):
    bdpm_dict = {}
    with open(file_path, encoding="latin1") as f:
        for line in f:
            parts = line.strip().split("\t")
            if len(parts) > 1:
                cis_code = parts[0]
                full_name = normalize_name(parts[1])
                bdpm_dict[full_name] = cis_code
    return bdpm_dict

# ----------------------
# Recherche floue pour trouver le code CIS correspondant
# ----------------------
def find_cis_fuzzy(drug_name, bdpm_dict, threshold=80):
    best_match = None
    best_score = 0
    for bdpm_name, cis in bdpm_dict.items():
        score = fuzz.partial_ratio(drug_name, bdpm_name)
        if score > best_score and score >= threshold:
            best_score = score
            best_match = cis
    return best_match

# ----------------------
# Extraire les interactions avec correspondance floue
# ----------------------
def extract_interactions(text, bdpm_dict, threshold=80):
    words = normalize_name(text).split()
    found = set()
    for w in words:
        cis = find_cis_fuzzy(w, bdpm_dict, threshold)
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

    with open("data/raw/raw_openfda.csv", newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            drug_name = normalize_name(row["drug"])
            cis_code = find_cis_fuzzy(drug_name, bdpm_dict, threshold=80)
            if not cis_code:
                continue  # ignorer si pas trouvé
            interactions = extract_interactions(row.get("interactions_text", ""), bdpm_dict, threshold=80)
            cleaned_records.append((cis_code, interactions))

    output_path = "data/raw/clean_openfda_bdpm_fuzzy.csv"
    with open(output_path, "w", newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(["drug_code", "interactions"])
        for cis, inter in cleaned_records:
            w.writerow([cis, ";".join(inter)])

    print(f"CSV nettoyé '{output_path}' généré avec {len(cleaned_records)} médicaments reconnus.")
