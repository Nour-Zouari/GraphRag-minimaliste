#tester avec questions sans recours à gemini => sans expiration d'API key
from neo4j import GraphDatabase

# Config Neo4j
uri = "bolt://localhost:7687"
user = "neo4j"
password = "123456789"
driver = GraphDatabase.driver(uri, auth=(user, password))

# Récupérer entités
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

# Vérifier interaction entre deux médicaments
def query_interaction(m1, m2):
    with driver.session() as session:
        result = session.run(
            """
            MATCH (a:MEDICAMENT {name:$m1})-[:INTERAGIT_AVEC]-(b:MEDICAMENT {name:$m2})
            RETURN a.name AS A, b.name AS B
            """,
            m1=m1, m2=m2
        )
        return result.single() is not None

# Vérifier allergie
def query_allergy(patient, allergen):
    with driver.session() as session:
        result = session.run(
            """
            MATCH (p:PATIENT {name:$patient})-[:A_ALLERGIE]->(a:ALLERGENE {name:$allergen})
            RETURN a.name AS A
            """,
            patient=patient, allergen=allergen
        )
        return result.single() is not None

# Simulation de questions automatiques
def test_chatbot():
    meds, allergens, patients = get_entities_from_graph()

    test_questions = [
        ("Est-ce que Aspirin interagit avec Ibuprofen ?", "interaction", ["Aspirin", "Ibuprofen"]),
        ("Patient1 est-il allergique à Penicillin ?", "allergy", ["Patient1", "Penicillin"]),
        ("Paracetamol interagit-il avec Aspirin ?", "interaction", ["Paracetamol", "Aspirin"]),
        ("Patient2 est-il allergique à Lactose ?", "allergy", ["Patient2", "Lactose"])
    ]

    for q, qtype, entities in test_questions:
        if qtype == "interaction":
            m1, m2 = entities
            if query_interaction(m1, m2):
                print(f"Question: {q}\nRéponse: Oui, {m1} interagit avec {m2}.\n")
            else:
                print(f"Question: {q}\nRéponse: Aucune interaction connue entre {m1} et {m2}.\n")
        elif qtype == "allergy":
            patient, allergen = entities
            if query_allergy(patient, allergen):
                print(f"Question: {q}\nRéponse: {patient} est allergique à {allergen}.\n")
            else:
                print(f"Question: {q}\nRéponse: Aucune allergie connue pour {patient} avec {allergen}.\n")

if __name__ == "__main__":
    test_chatbot()
