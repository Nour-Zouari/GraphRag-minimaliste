# MedicalChatbot (starter)

This small skeleton provides a minimal project layout to build a medical
chatbot that uses a graph database (Neo4j) and LangChain for LLM orchestration.

Structure:

- `data/` — optional raw data files (csv, txt)
- `graph/` — scripts to populate and interact with Neo4j
- `langchain_pipeline/` — LangChain-based chatbot logic
- `requirements.txt` — Python dependencies
- `main.py` — small runner script

Quick start (Windows PowerShell):

```powershell
cd ".../GraphRag-minimaliste/MedicalChatbot"
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
# Configure Neo4j env vars (optional)
$env:NEO4J_URI = 'bolt://localhost:7687'
$env:NEO4J_USER = 'neo4j'
$env:NEO4J_PASSWORD = 'password'
python graph/build_graph.py
python main.py
```

Next steps:
- Implement retrieval and vector store in `langchain_pipeline/chatbot.py`.
- Expand `graph/build_graph.py` to load real medication/allergy data.
- Add tests and CI as needed.


### NB : Le fichier test_graph.py que n’envoie aucune requête à Gemini => pas d'épuisement de quota avec ce fichier
Il se connecte uniquement à Neo4j via GraphDatabase.driver.
Il lit les nœuds et relations dans le graphe et imprime les résultats dans la console.
Il ne contient aucun appel à genai.generate_text() ou toute autre fonction Gemini.
=> Résultat : aucune tentative gratuite Gemini ne sera consommée en exécutant ce fichier.
Tu peux le lancer autant de fois que tu veux sans épuiser ton quota Gemi

Ce qui change dans chatbot_efficient.py :
Extraction plus robuste des médicaments et allergènes avec regex.
Détection automatique du patient si mentionné dans la question.
Gemini n’est appelé que si Neo4j ne fournit aucune réponse.
Historique complet des questions/réponses pour chaque session.
Messages d’info pour savoir quand Gemini est sollicité.

| Aspect                  | Fichier `test_interactions/test_allergies` | Fichier `test_chatbot()`                               |
| ----------------------- | ------------------------------------------ | ------------------------------------------------------ |
| But                     | Vérifier que les données existent          | Vérifier que le chatbot répond correctement            |
| Affichage               | Montre **tout le graphe**                  | Montre **réponses simulées aux questions**             |
| Interaction utilisateur | Non                                        | Non interactif, mais simule des questions              |
| Gemini                  | Non                                        | Non                                                    |
| Utilité                 | Débogage et inspection du graphe           | Validation du comportement du chatbot avant usage réel |
