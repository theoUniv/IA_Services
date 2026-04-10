# ⚙️ Backend API - Serveur Python

Ceci est le code du serveur (backend) du projet "Tennis Vision".
Il a été dev avec **FastAPI** pour être rapide à coder et parce que la doc interactive (Swagger) se génère toute seule.

## Comment gérer ça sans Docker ? (Mode local)

1. Vous allez dans le dossier backend :
   ```bash
   cd backend
   ```
2. Vous installez les librairies :
   ```bash
   pip install -r requirements.txt
   ```
3. Vous lancez votre serveur avec Uvicorn :
   ```bash
   uvicorn api.main:app --reload
   ```

## Les 3 supers endpoints

- `POST /predict/vision` : Celui-ci interroge notre modèle `modele_tennis_vision.keras` d'apprentissage profond pour deviner le type de coup (coup droit, revers, etc.).
- `POST /predict/llm` : Celui-là c'est l'option "IA générative" qui envoie la photo à un grand modèle de langage via OpenRouter pour faire la même analyse.
- `POST /predict/match` : **Nouveau !** Ce serveur mouline les stats de l'ATP pour prédire le gagnant d'un match entre deux joueurs sur une surface précise.

PS : Il ne faut pas oublier d'entrer la clé API dans OpenRouter
