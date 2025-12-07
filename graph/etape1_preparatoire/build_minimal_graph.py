# ceci est pour un test minimaliste du graphe médical => pas notre code final
from neo4j import GraphDatabase

uri = "bolt://localhost:7687"
user = "neo4j"
password = "123456789"  # remplace par ton mot de passe Neo4j
driver = GraphDatabase.driver(uri, auth=(user, password))

def populate_graph(tx):
    # Médicaments
    tx.run("MERGE (m:MEDICAMENT {name:'Aspirin'})")
    tx.run("MERGE (m:MEDICAMENT {name:'Ibuprofen'})")
    tx.run("MERGE (m:MEDICAMENT {name:'Paracetamol'})")
    # Allergènes
    tx.run("MERGE (a:ALLERGENE {name:'Penicillin'})")
    # Patient
    tx.run("MERGE (p:PATIENT {name:'Patient1'})")
    # Interactions médicamenteuses
    tx.run("""
    MATCH (a:MEDICAMENT {name:'Aspirin'}), (b:MEDICAMENT {name:'Ibuprofen'})
    MERGE (a)-[:INTERAGIT_AVEC]->(b)
    """)
    # Allergies
    tx.run("""
    MATCH (p:PATIENT {name:'Patient1'}), (a:ALLERGENE {name:'Penicillin'})
    MERGE (p)-[:A_ALLERGIE]->(a)
    """)

if __name__ == "__main__":
    with driver.session() as session:
        session.execute_write(populate_graph)  # fonctionne pour Neo4j driver v5+
    print("Graphe médical initialisé dans Neo4j.")
