import os
import google.generativeai as genai
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()
# Config Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Config Neo4j
uri = "bolt://localhost:7687"
user = "neo4j"
password = "123456789"
driver = GraphDatabase.driver(uri, auth=(user, password))

# Récupérer tous les médicaments et allergènes connus dans le graphe
def get_entities_from_graph():
    meds = []
    allergens = []
    with driver.session() as session:
        result = session.run("MATCH (m:MEDICAMENT) RETURN m.name AS name")
        meds = [record["name"] for record in result]
        result = session.run("MATCH (a:ALLERGENE) RETURN a.name AS name")
        allergens = [record["name"] for record in result]
    return meds, allergens

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

# Vérifier allergie pour un patient
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

# Fonction principale pour répondre
def respond(user_question: str):
    meds, allergens = get_entities_from_graph()

    # Identifier les médicaments mentionnés
    found_meds = [m for m in meds if m.lower() in user_question.lower()]
    if len(found_meds) == 2:
        m1, m2 = found_meds
        if query_interaction(m1, m2):
            return f"D'après mes données, {m1} interagit avec {m2} — ce n'est pas recommandé."
        else:
            return f"Aucune interaction connue dans ma base entre {m1} et {m2}."

    # Identifier allergènes et patient
    found_allergens = [a for a in allergens if a.lower() in user_question.lower()]
    if len(found_allergens) == 1:
        allerg = found_allergens[0]
        patient = "Patient1"  # ici tu peux demander le nom ou extraire depuis la phrase
        if query_allergy(patient, allerg):
            return f"{patient} est allergique à {allerg}."
        else:
            return f"Aucune allergie connue pour {patient} avec {allerg}."

    # Sinon : demander à Gemini pour une réponse prudente
    model = genai.GenerativeModel("gemini-2.5-flash") # Create model instance
    prompt_text = f"Utilisateur: {user_question}\nAssistant: Réponds de manière prudente si tu n'as pas l'information."
    response = model.generate_content(prompt_text) # Use generate_content
    return response.text

# Test rapide
if __name__ == "__main__":
    print("Chatbot médical prêt (Gemini + Neo4j)")
    while True:
        q = input("Question: ")
        if q.lower() in ["exit", "quit"]:
            break
        print("Réponse:", respond(q))
