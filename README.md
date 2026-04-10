# 🎾 Projet Deep Learning - IA Services (Tennis Vision)

Bienvenue sur notre repo de rendu pour le projet "IA Services".

## Les 3 supers endpoints

- `POST /predict/vision` : Celui-ci interroge notre modèle `modele_tennis_vision.keras` d'apprentissage profond pour deviner le type de coup (coup droit, revers, etc.).
- `POST /predict/llm` : Celui-là c'est l'option "IA générative" qui envoie la photo à un grand modèle de langage via OpenRouter pour faire la même analyse.
- `POST /predict/match` : **Le petit nouveau !** Il prend les noms de deux joueurs ATP, mouline les stats historiques (classement, win rate lissé, etc.) et prédit qui va gagner le match sur une surface donnée.

## L'architecture du projet

Au lieu de tout balancer dans un seul dossier, nous avons tout séparé en deux pour faire ça proprement (comme dans l'industrie) :

- **`/backend`** : C'est là que tourne l'API sous FastAPI et qu'on charge notre modèle Keras. Y'a aussi la logique pour l'API LLM (OpenRouter) et maintenant un nouveau système de prédiction de matchs ATP basé sur les stats historiques.
- **`/frontend`** : C'est une petite interface stylée faite avec React (Vite) pour qu'on puisse juste "drag & drop" une image ou simuler un match de tennis et avoir le résultat de la prédiction sans passer par Postman/Swagger. (D'ailleurs le frontend a son propre README dedans si tu veux voir comment nous l'avons monté).

## Ce que ça fait

- Vous avez une zone de **Drag & Drop** pour uploader l'image du joueur et savoir s'il fait un revers, un service, etc.
- Vous avez un nouvel onglet **"Prédiction Match ATP"** : vous tapez le nom de deux joueurs (genre Federer vs Nadal), vous choisissez la surface, et l'IA vous dit qui a le plus de chances de gagner en se basant sur tout l'historique de l'ATP !
- Vous pouvez choisir si vous voulez faire la prédiction vision avec le **Modèle Keras/TensorFlow** qu'on a entraîné, ou bien tester avec l'**API externe OpenRouter** (LLM).
- Ça fait un appel vers le backend (qui tourne sur le port 3500 via Docker), et ça vous affiche une belle interface avec les résultats.

## Comment on teste ?

Nous avons tout dockerisé (frontend + backend). Donc pas besoin d'installer Python ou Node sur ta machine, il te faut juste **Docker**

Pour tout lancer (ça va build les images et démarrer les deux serveurs en un coup) :
```bash
docker-compose up --build
```
*(Attention : le premier build peut prendre un peu de temps parce que TensorFlow est énorme à télécharger, c'est normal).*

Une fois que la console affiche que l'application est prête, tu as juste à aller sur ton navigateur :
👉 **L'application web** : [http://localhost:3000](http://localhost:3000)
👉 **Le Swagger API (pour les curieux)** : [http://localhost:8000/docs](http://localhost:8000/docs)

## Note sur l'API externe (OpenRouter)

Pour que l'inférence via l'Intelligence Artificielle LLM (la 2ème option dans l'interface) fonctionne correctement, il faut glisser une clé OpenAI/OpenRouter dans le fichier `backend/.env`. Nous avons configuré `docker-compose.yml` pour qu'il la récupère et la donne automatiquement au backend.

Merci d'avoir regardé notre projet.
