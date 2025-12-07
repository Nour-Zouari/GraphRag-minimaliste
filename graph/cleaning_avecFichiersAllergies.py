import pandas as pd
import unicodedata
import re

# -----------------------------
# Charger la liste des allergènes
# -----------------------------
def load_allergens(path="data/raw/allergies.csv"):
    """
    Charge le fichier CSV des allergènes (colonne 'allergen')
    et renvoie un set de noms normalisés (en majuscules, espaces standardisés)
    """
    df = pd.read_csv(path)
    allergens = df["allergen"].str.upper().str.replace("_", " ").tolist()
    return set(allergens)

# -----------------------------
# Normalisation du texte
# -----------------------------
def normalize_text(text):
    if not isinstance(text, str):
        return ""
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ASCII", "ignore").decode("utf-8")
    text = text.upper()
    text = re.sub(r"[^A-Z0-9 ]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

# -----------------------------
# Extraire interactions allergène ↔ médicament
# -----------------------------
def extract_allergy_relations(df_openfda, allergens):
    rows = []

    for _, row in df_openfda.iterrows():
        drug_name = normalize_text(row["drug"])
        text_content = normalize_text(row.get("interactions_text", ""))

        for allergen in allergens:
            if allergen in text_content:
                rows.append({
                    "medicament": drug_name,
                    "allergen": allergen
                })

    return pd.DataFrame(rows).drop_duplicates()

# -----------------------------
# Programme principal
# -----------------------------
def run():
    allergens = load_allergens()
    df_openfda = pd.read_csv("data/raw/raw_openfda.csv")

    df_relations = extract_allergy_relations(df_openfda, allergens)
    df_relations.to_csv("data/processed/allergies_medicaments_clean.csv", index=False)

    print(f"Extraction terminée : {len(df_relations)} interactions trouvées.")
    if len(df_relations) > 0:
        print(df_relations.head())

if __name__ == "__main__":
    run()
