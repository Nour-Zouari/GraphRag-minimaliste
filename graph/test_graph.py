# tester les données seulement sans questions
from neo4j import GraphDatabase

# Config Neo4j
uri = "bolt://localhost:7687"
user = "neo4j"
password = "123456789"  # adapte selon ton installation
driver = GraphDatabase.driver(uri, auth=(user, password))

# Récupérer tous les médicaments et allergènes connus dans le graphe
def get_entities_from_graph():
    meds = []
    allergens = []
    patients = []
    with driver.session() as session:
        result = session.run("MATCH (m:MEDICAMENT) RETURN m.name AS name")
        meds = [record["name"] for record in result]

        result = session.run("MATCH (a:ALLERGENE) RETURN a.name AS name")
        allergens = [record["name"] for record in result]

        result = session.run("MATCH (p:PATIENT) RETURN p.name AS name")
        patients = [record["name"] for record in result]

    return meds, allergens, patients

# Vérifier interactions
def test_interactions():
    with driver.session() as session:
        result = session.run("""
        MATCH (a:MEDICAMENT)-[r:INTERAGIT_AVEC]-(b:MEDICAMENT)
        RETURN a.name AS A, b.name AS B, r.info AS info
        """)
        interactions = result.values()
        if interactions:
            print("=== Interactions médicamenteuses dans le graphe ===")
            for a, b, info in interactions:
                print(f"{a} <-> {b} : {info}")
        else:
            print("Aucune interaction trouvée dans le graphe.")

# Vérifier allergies
def test_allergies():
    with driver.session() as session:
        result = session.run("""
        MATCH (p:PATIENT)-[:A_ALLERGIE]->(a:ALLERGENE)
        RETURN p.name AS Patient, a.name AS Allergen
        """)
        allergies = result.values()
        if allergies:
            print("\n=== Allergies connues dans le graphe ===")
            for patient, allergen in allergies:
                print(f"{patient} est allergique à {allergen}")
        else:
            print("Aucune allergie trouvée dans le graphe.")

if __name__ == "__main__":
    meds, allergens, patients = get_entities_from_graph()
    print("Médicaments détectés :", meds)
    print("Allergènes détectés :", allergens)
    print("Patients détectés :", patients)

    test_interactions()
    test_allergies()
