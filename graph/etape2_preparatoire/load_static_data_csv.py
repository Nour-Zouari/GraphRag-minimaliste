from neo4j import GraphDatabase

# Config Neo4j
uri = "bolt://localhost:7687"
user = "neo4j"
password = "123456789"  # change selon ton installation
driver = GraphDatabase.driver(uri, auth=(user, password))

# Chemin vers le dossier CSV (adapté selon ton système)
import_path = "C:/Users/zouar/.Neo4jDesktop2/Data/dbmss/dbms-639ee1cc-508c-4a8a-965e-4c8f7dc33d54/import/"

def load_medicaments(tx):
    tx.run(f"""
    LOAD CSV WITH HEADERS FROM "file:///{import_path}medicaments.csv" AS row
    MERGE (m:MEDICAMENT {{name: row.name}})
    SET m.active_principle = row.active_principle;
    """)

def load_interactions(tx):
    tx.run(f"""
    LOAD CSV WITH HEADERS FROM "file:///{import_path}interactions.csv" AS row
    MATCH (a:MEDICAMENT {{name: row.m1}})
    MATCH (b:MEDICAMENT {{name: row.m2}})
    MERGE (a)-[:INTERAGIT_AVEC {{info: row.description}}]-(b);
    """)

def load_allergies(tx):
    tx.run(f"""
    LOAD CSV WITH HEADERS FROM "file:///{import_path}allergies.csv" AS row
    MERGE (p:PATIENT {{name: row.patient}})
    MERGE (a:ALLERGENE {{name: row.allergen}})
    MERGE (p)-[:A_ALLERGIE]->(a);
    """)

with driver.session() as session:
    session.write_transaction(load_medicaments)
    session.write_transaction(load_interactions)
    session.write_transaction(load_allergies)

print("Import des CSV terminé et graphe prêt.")
