# 🎾 Projet Deep Learning - IA Services (Tennis Vision)

Bienvenue sur notre repo de rendu pour le projet "IA Services".
Le but du projet c'était de créer une application capable de classifier des images de coups de tennis (coup droit, revers, service, ou position d'attente). 

## L'architecture du projet

Au lieu de tout balancer dans un seul dossier, nous avons tout séparé en deux pour faire ça proprement (comme dans l'industrie) :

- **`/backend`** : C'est là que tourne l'API sous FastAPI et qu'on charge notre modèle Keras. Y'a aussi la logique pour l'API LLM (OpenRouter).
- **`/frontend`** : C'est une petite interface stylée faite avec React (Vite) pour qu'on puisse juste "drag & drop" une image et avoir le résultat de la prédiction sans passer par Postman/Swagger. (D'ailleurs le frontend a son propre README dedans si tu veux voir comment nous l'avons monté).

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
