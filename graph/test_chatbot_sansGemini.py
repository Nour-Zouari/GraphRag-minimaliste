import os
import unicodedata
import re
from neo4j import GraphDatabase
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
# --- Config Gemini ---
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# --- Config Neo4j ---
uri = "bolt://localhost:7687"
user = "neo4j"
password = "123456789"
driver = GraphDatabase.driver(uri, auth=(user, password))

# ----------------------
# Normalisation des noms
# ----------------------
def normalize_text(text):
    text = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('utf-8')
    text = text.upper()
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

# ----------------------
# Récupérer toutes les entités depuis Neo4j
# ----------------------
def get_entities_from_graph():
    med_mapping = {}  # nom normalisé -> (code, nom original)
    allergen_mapping = {}  # nom normalisé -> (code, nom original)
    with driver.session() as session:
        result = session.run("MATCH (m:MEDICAMENT) RETURN m.code AS code, m.name AS name")
        for record in result:
            norm_name = normalize_text(record["name"])
            med_mapping[norm_name] = (record["code"], record["name"])
        result = session.run("MATCH (a:ALLERGENE) RETURN a.code AS code, a.name AS name")
        for record in result:
            norm_name = normalize_text(record["name"])
            allergen_mapping[norm_name] = (record["code"], record["name"])
    return med_mapping, allergen_mapping

# ----------------------
# Requêtes Neo4j
# ----------------------
def query_interaction(code1, code2):
    with driver.session() as session:
        result = session.run(
            "MATCH (a:MEDICAMENT {code:$c1})-[:INTERAGIT_AVEC]-(b:MEDICAMENT {code:$c2}) "
            "RETURN a.code AS A, b.code AS B",
            c1=code1, c2=code2
        )
        return result.single() is not None

def query_allergy(patient, allergen_code):
    with driver.session() as session:
        result = session.run(
            "MATCH (p:PATIENT {name:$patient})-[:A_ALLERGIE]->(a:ALLERGENE {code:$allergen}) "
            "RETURN a.code AS A",
            patient=patient, allergen=allergen_code
        )
        return result.single() is not None

# ----------------------
# Fonction principale pour répondre
# ----------------------
def respond(user_question: str, patient="Patient1"):
    user_question_norm = normalize_text(user_question)
    med_mapping, allergen_mapping = get_entities_from_graph()

    # Identifier les médicaments mentionnés
    found_meds = [
        (code, name) for norm_name, (code, name) in med_mapping.items()
        if norm_name in user_question_norm
    ]
    if len(found_meds) >= 2:
        for i in range(len(found_meds)):
            for j in range(i+1, len(found_meds)):
                code1, name1 = found_meds[i]
                code2, name2 = found_meds[j]
                if query_interaction(code1, code2):
                    return f"D'après mes données, {name1} interagit avec {name2} — ce n'est pas recommandé."
        return "Aucune interaction connue entre les médicaments mentionnés."

    # Identifier les allergènes mentionnés
    found_allergens = [
        (code, name) for norm_name, (code, name) in allergen_mapping.items()
        if norm_name in user_question_norm
    ]
    if found_allergens:
        allerg_code, allerg_name = found_allergens[0]
        if query_allergy(patient, allerg_code):
            return f"{patient} est allergique à {allerg_name}."
        else:
            return f"Aucune allergie connue pour {patient} avec {allerg_name}."

    return "Je n'ai pas trouvé d'informations pertinentes dans ma base de données."
    # Sinon : demander à Gemini pour une réponse prudente
    model = genai.GenerativeModel("gemini-2.5-flash")
    prompt_text = f"Utilisateur: {user_question}\nAssistant: Réponds de manière prudente si tu n'as pas l'information."
    response = model.generate_content(prompt_text)
    return response.text

# ----------------------
# Boucle interactive
# ----------------------
if __name__ == "__main__":
    print("Chatbot médical prêt (Gemini + Neo4j)")
    while True:
        q = input("Question: ")
        if q.lower() in ["exit", "quit"]:
            break
        print("Réponse:", respond(q))
