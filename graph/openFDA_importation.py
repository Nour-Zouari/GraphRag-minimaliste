import requests
import csv

def download_openfda(limit=500):
    """
    Télécharge des labels depuis openFDA (médicaments et interactions)
    """
    url = f"https://api.fda.gov/drug/label.json?search=drug_interactions:*&limit={limit}"
    resp = requests.get(url)
    resp.raise_for_status()
    data = resp.json()
    return data.get("results", [])

def parse_label(label):
    """
    Récupère le nom principal et le texte des interactions
    """
    names = label.get("openfda", {}).get("generic_name") or label.get("openfda", {}).get("brand_name")
    if not names:
        return None, []
    med = names[0]
    interactions_texts = label.get("drug_interactions", [])
    text = " ".join(interactions_texts)
    return med, text

if __name__ == "__main__":
    labels = download_openfda(limit=500)
    processed = [parse_label(lbl) for lbl in labels if parse_label(lbl)[0]]
    
    with open("data/raw/raw_openfda.csv", "w", newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(["drug", "interactions_text"])
        for med, text in processed:
            w.writerow([med, text])
    
    print("CSV brut 'raw_openfda.csv' généré avec", len(processed), "médicaments.")
