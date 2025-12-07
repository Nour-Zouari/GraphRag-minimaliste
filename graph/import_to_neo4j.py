import csv
import re
import unicodedata
from neo4j import GraphDatabase

# --- Config Neo4j ---
uri = "bolt://localhost:7687"
user = "neo4j"
password = "123456789"
driver = GraphDatabase.driver(uri, auth=(user, password))

def normalize_name(name):
    name = unicodedata.normalize('NFKD', name).encode('ASCII', 'ignore').decode('utf-8')
    name = name.upper()
    name = re.sub(r'[^\w\s/-]', ' ', name)
    name = re.sub(r'\s+', ' ', name).strip()
    return name

def simplify_name(name):
    name = normalize_name(name)
    parts = name.split()
    if not parts:
        return "INCONNU"
    return parts[0]

def clear_neo4j():
    with driver.session() as session:
        session.run("MATCH (n) DETACH DELETE n")
        print("Base Neo4j vidée.")

def load_bdpm(file_path="data/raw/CIS_bdpm.txt"):
    bdpm_dict = {}
    with open(file_path, encoding="latin1") as f:
        for line in f:
            parts = line.strip().split("\t")
            if len(parts) > 1:
                code, nom = parts[0], parts[1]
                bdpm_dict[code] = simplify_name(nom)
    return bdpm_dict

def load_clean_csv(file_path="data/processed/clean_openfda_bdpm.csv"):
    records = []
    with open(file_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            drug_code = row["drug_code"]
            interactions = row["interactions"].split(";") if row["interactions"] else []
            interactions = [x for x in interactions if x != drug_code]
            records.append((drug_code, interactions))
    return records

def add_medicament(tx, code, name):
    tx.run(
        "MERGE (m:MEDICAMENT {code:$code}) "
        "SET m.name=$name",
        code=code, name=name
    )

def add_medicaments_batch(tx, codes, bdpm_dict):
    tx.run(
        """
        UNWIND $codes AS c
        MERGE (m:MEDICAMENT {code:c})
        SET m.name=$names[c]
        """,
        codes=codes,
        names=bdpm_dict
    )

def add_interactions_batch(tx, drug_code, interaction_codes):
    if not interaction_codes:
        return
    tx.run(
        """
        MATCH (a:MEDICAMENT {code:$drug})
        MATCH (b:MEDICAMENT) WHERE b.code IN $codes
        MERGE (a)-[:INTERAGIT_AVEC]->(b)
        """,
        drug=drug_code,
        codes=interaction_codes
    )

def import_to_neo4j(records, bdpm_dict):
    with driver.session() as session:
        all_drug_codes = set([code for code, _ in records])
        for _, interactions in records:
            all_drug_codes.update(interactions)
        session.execute_write(add_medicaments_batch, list(all_drug_codes), bdpm_dict)
        for drug_code, interactions in records:
            session.execute_write(add_interactions_batch, drug_code, interactions)

if __name__ == "__main__":
    clear_neo4j()
    bdpm_dict = load_bdpm()
    records = load_clean_csv()
    print(f"Import de {len(records)} médicaments dans Neo4j...")
    import_to_neo4j(records, bdpm_dict)
    print("Import terminé.")
