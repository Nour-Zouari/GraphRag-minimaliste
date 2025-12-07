# MedicalChatbot

This provides a project layout to build a medical chatbot that uses a graph database (Neo4j) and LangChain for LLM orchestration.

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
Tu peux le lancer autant de fois que tu veux sans épuiser ton quota Gemini
=> pour vérifier que Neo4j a bien chargé les CSV.

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

### le fichier build_graph.py :
ceci est pour un test minimaliste du graphe médical => pas notre code final



## Cas de test avec Gemini : 
> python main.py 
Chatbot médical (Gemini + Neo4j)
Question: Est-ce que le médicament "Metformin" interagit avec "Aspirin" ?
Réponse: Oui, il existe une **interaction potentielle** entre la Metformin et l'Aspirin, bien que la co-administration soit **fréquente et généralement considérée comme sûre** pour la plupart des patients, surtout avec de l'aspirine à faible dose.

Voici les points importants à considérer :

1.  **L'interaction principale concerne la fonction rénale :**
    *   **L'aspirine (surtout à des doses plus élevées ou en utilisation chronique)** peut, dans certains cas, affecter la fonction rénale (reins).
    *   **La Metformin** est principalement éliminée du corps par les reins.
    *   Si la fonction rénale est altérée, la Metformin peut s'accumuler dans le corps, ce qui augmente le risque (rare mais grave) d'acidose lactique.

2.  **Hypoglycémie (faible taux de sucre dans le sang) :**
    *   Bien que moins préoccupant avec la Metformin seule, certains anti-inflammatoires non stéroïdiens (AINS) dont l'aspirine à dose élevée, peuvent potentiellement augmenter l'effet hypoglycémiant d'autres médicaments antidiabétiques. Ce n'est généralement pas un problème majeur avec la Metformin qui agit différemment des sulfonylurées par exemple.

**En résumé :**

*   **Aspirine à faible dose (pour la protection cardiovasculaire) :** Elle est très souvent utilisée en toute sécurité avec la Metformin sous surveillance médicale.
*   **Aspirine à dose plus élevée (pour la douleur, l'inflammation) ou usage chronique :** Le risque d'altération de la fonction rénale est plus élevé, et par conséquent, le risque d'accumulation de Metformin.

**Recommandation prudente :**

**Il est impératif de toujours informer votre médecin ou votre pharmacien de TOUS les médicaments que vous prenez**, y compris les médicaments en vente libre comme l'aspirine. Votre professionnel de la santé pourra évaluer votre fonction rénale, vos autres conditions médicales et déterminer si cette combinaison est appropriée pour vous, en ajustant les doses si nécessaire ou en surveillant attentivement. 

**Je suis un programme d'IA et ne peux pas fournir de conseils médicaux. Cette information ne remplace en aucun cas l'avis d'un professionnel de la santé.**


## on a telechager la dataset BPDM cis-pathologie : https://explore.data.gouv.fr/fr/datasets/62694159aefe65020a033bdc/#/resources/f549a488-d0fb-4ded-8fe0-1bbd6f5653bd
pourquoi l'utiliser ? 


## limites et ouverture d'horizons :
Dans le CSV OpenFDA ou des sources similaires, la **deuxième colonne (“interactions_text” ou équivalent)** peut contenir :

* Des interactions connues avec d’autres médicaments
* Des effets secondaires, précautions ou notes générales
* Des mentions contextuelles qui ne signifient pas forcément qu’il y a une interaction directe avec le médicament de la première colonne

Donc **tous les noms détectés dans le texte ne sont pas forcément des interactions actives** avec le médicament principal.

Pour plus de précision :

1. Si on veut **la sécurité**, on peut garder uniquement les lignes où le texte contient explicitement des mots comme `interact`, `contraindicated`, `avoid`, etc., en anglais.
2. Les mentions passives ou générales seraient ignorées, sinon on risque d’avoir beaucoup de faux positifs.
3. Une autre approche consiste à **consulter une base de données spécialisée d’interactions médicamenteuses** pour valider les relations. Le CSV OpenFDA peut servir de point de départ, mais il n’est pas parfait pour générer un graphe d’interactions fiable à 100 %.
On pourrait un jour  **filtrer le texte pour ne garder que les interactions probables et générer le CSV Neo4j sans trop de “bruit”**.

## remarque concernant l'importation dans neo4j : 
Le code CIS dans Neo4j sert surtout à identifier de manière unique chaque médicament. Dans une base graphique, tu veux que chaque nœud soit un identifiant clair et stable, pas juste un nom qui peut avoir des variantes (ex. : « Paracetamol », « Paracétamol », « PARACETAMOL 500 mg »).

En pratique :
Nom du médicament → affichage lisible pour l’utilisateur ou pour recherche
Code CIS → clé unique pour le nœud dans Neo4j, pour relier correctement les interactions et éviter les doublons
Relations (INTERAGIT_AVEC) → entre nœuds identifiés par Code_CIS