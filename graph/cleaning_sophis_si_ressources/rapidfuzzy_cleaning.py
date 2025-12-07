import csv
import re
import unicodedata
from rapidfuzz import process, fuzz

# ----------------------
# Normalisation des noms
# ----------------------
def normalize_name(name):
    if not name:
        return ""
    # enlever accents
    name = unicodedata.normalize('NFKD', name).encode('ASCII', 'ignore').decode('utf-8')
    # tout en majuscules
    name = name.upper()
    # remplacer ponctuation par espace
    name = re.sub(r'[^\w\s]', ' ', name)
    # supprimer espaces multiples
    name = re.sub(r'\s+', ' ', name).strip()
    return name

# ----------------------
# Charger BDPM et construire dictionnaire nom complet → code CIS
# ----------------------
def load_bdpm(file_path="data/raw/CIS_bdpm.txt"):
    bdpm_dict = {}
    with open(file_path, encoding="latin1") as f:
        for line in f:
            parts = line.strip().split("\t")
            if len(parts) > 1:
                cis_code = parts[0]
                nom = normalize_name(parts[1])
                bdpm_dict[nom] = cis_code
    return bdpm_dict

# ----------------------
# Extraire les interactions dans le texte
# ----------------------
def extract_interactions(text, bdpm_names, bdpm_dict, threshold=80):
    text_norm = normalize_name(text)
    found = set()
    # chercher correspondances floues avec les noms BDPM
    matches = process.extract(
        text_norm,
        bdpm_names,
        scorer=fuzz.partial_ratio,
        score_cutoff=threshold,
        limit=None
    )
    for match_name, score, _ in matches:
        found.add(bdpm_dict[match_name])
    return list(found)

# ----------------------
# Traitement principal
# ----------------------
if __name__ == "__main__":
    bdpm_dict = load_bdpm("data/raw/CIS_bdpm.txt")
    bdpm_names = list(bdpm_dict.keys())
    print(f"Dictionnaire BDPM chargé avec {len(bdpm_dict)} médicaments.")

    cleaned_records = []

    with open("data/raw/raw_openfda.csv", newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            drug_name = normalize_name(row["drug"])
            # recherche floue du médicament dans BDPM
            match = process.extractOne(drug_name, bdpm_names, scorer=fuzz.partial_ratio, score_cutoff=80)
            if not match:
                continue
            matched_name = match[0]
            cis_code = bdpm_dict[matched_name]
            # extraire interactions floues dans le texte
            interactions = extract_interactions(row.get("interactions_text", ""), bdpm_names, bdpm_dict)
            cleaned_records.append((cis_code, interactions))

    output_path = "data/raw/clean_openfda_bdpm.csv"
    with open(output_path, "w", newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(["drug_code", "interactions"])
        for cis, inter in cleaned_records:
            w.writerow([cis, ";".join(inter)])

    print(f"CSV nettoyé '{output_path}' généré avec {len(cleaned_records)} médicaments reconnus.")
