import csv
from neo4j import GraphDatabase
import os

# --- Config Neo4j ---
uri = "bolt://localhost:7687"
user = "neo4j"
password = "123456789"
driver = GraphDatabase.driver(uri, auth=(user, password))

# --- Chargement CSV nettoyé ---
def load_clean_csv(file_path="data/processed/clean_openfda_bdpm.csv"):
    records = []
    with open(file_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            drug_code = row["drug_code"]
            interactions = row["interactions"].split(";") if row["interactions"] else []
            records.append((drug_code, interactions))
    return records

# --- Fonctions pour Neo4j ---
def create_medicament(tx, code_cis):
    tx.run("MERGE (m:MEDICAMENT {code:$code})", code=code_cis)

def create_interaction(tx, code1, code2):
    tx.run("""
        MATCH (a:MEDICAMENT {code:$code1})
        MATCH (b:MEDICAMENT {code:$code2})
        MERGE (a)-[:INTERAGIT_AVEC]->(b)
        """, code1=code1, code2=code2)

# --- Import dans Neo4j ---
def import_to_neo4j(records):
    with driver.session() as session:
        for drug_code, interactions in records:
            session.write_transaction(create_medicament, drug_code)
            for inter_code in interactions:
                session.write_transaction(create_medicament, inter_code)
                session.write_transaction(create_interaction, drug_code, inter_code)

if __name__ == "__main__":
    os.makedirs("data/processed", exist_ok=True)
    records = load_clean_csv()
    print(f"Import de {len(records)} médicaments dans Neo4j...")
    import_to_neo4j(records)
    print("Import terminé avec succès.")
