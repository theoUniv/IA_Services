# 🎾 Frontend - Tennis Vision App 

Ceci est la partie Frontend de notre projet "Tennis Vision". Nous l'avons faite avec **React** (via Vite, parce que c'est super rapide) pour qu'on ait une interface super propre au lieu d'utiliser juste des routes API.

Nous avons essayé de donner un petit style moderne "Glassmorphism" au design, avec des couleurs sombres et un petit accent jaune fluo histoire de rappeler les balles de tennis.

## Comment ça marche ?

Normalement, **pas besoin de se prendre la tête**, nous avons tout mis dans le `docker-compose` à la racine du projet. Mais si jamais vous voulez juste lancer le front tout de suite (sans Docker) pour modifier le design :

1. Vous vous mettez dans le dossier `frontend` :
   ```bash
   cd frontend
   ```
2. Vous installes les dépendances (j'ai utilisé `axios` pour l'API et `lucide-react` pour les petites icônes sympa) :
   ```bash
   npm install
   ```
3. Vous lancez le serveur de dev :
   ```bash
   npm run dev
   ```

Après ça, le site tourne sur [http://localhost:3000](http://localhost:3000) (ou 5173 parfois s'il y a un conflit de port).

## Ce que ça fait
- **Analyse d'image** : Vous avez une zone de **Drag & Drop** pour uploader l'image du joueur. Vous pouvez choisir si vous voulez faire la prédiction avec le **Modèle Keras/TensorFlow** qu'on a entraîné, ou bien tester avec l'**API externe OpenRouter** (LLM). Ça vous affiche une belle jauge avec le score de confiance.
- **Prédiction de Match** : Dans le deuxième onglet, vous pouvez simuler un match entre deux joueurs de l'ATP. On utilise alors un moteur de stats historiques pour prédire qui va gagner !
- Ça fait un appel vers le backend (qui tourne sur le port 3500 via Docker), et l'interface s'occupe de tout vous afficher.
