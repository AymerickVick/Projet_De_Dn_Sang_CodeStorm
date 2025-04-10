# Projet Don de Sang

## Aperçu
 Bienvenue sur notre 🌟 **application web innovante** dédiée à la gestion des donneurs de sang ! 🩸 Conçue avec Django et équipée d'une interface moderne et responsive, notre plateforme centralise toutes les informations essentielles des donneurs (âge, genre, profession, localisation, santé, dons) et utilise un modèle de machine learning pour prédire l'éligibilité des donneurs. 📊 Grâce à des analyses statistiques détaillées et une palette de couleurs rouge et grise élégante, accompagnée d'icônes Font Awesome, notre application offre une expérience utilisateur fluide et attrayante. Rejoignez-nous pour rendre la gestion des dons de sang plus efficace et accessible ! 🚀


![image](https://github.com/user-attachments/assets/b0aacf86-86a0-4e5a-bd9c-68f44b09db5e)  


![image](https://github.com/user-attachments/assets/535c80ef-c4ca-4dde-b4a5-a68612bc5354)




## Objectifs 🎯
📊 Gérer les données des donneurs


- Centraliser et organiser les informations des donneurs de sang de manière efficace.


🔍 Prédire l’éligibilité via Machine Learning

- Utiliser des algorithmes de machine learning pour déterminer l'éligibilité des donneurs potentiels.
  
🖥️ Interface intuitive pour CRUD (ajouter, modifier, supprimer, analyser)

- Développer une interface conviviale permettant d'ajouter, modifier, supprimer et analyser les données des donneurs.
 
📍 Géolocalisation automatique


  - Intégrer des fonctionnalités de géolocalisation automatique pour faciliter la localisation des donneurs.

## Prérequis 🛠️
- **Framework web** : Django 4.2.16
🎯 Utilisé pour construire l'application web avec une architecture robuste et flexible.
- **Logiciels** :
  - 🐍 Python 3.9.6+ : Langage de programmation utilisé pour le développement de l'application.
  - 🌐 Navigateur web : Pour tester et utiliser l'application.
  - 🛠️ Git  : Pour le contrôle de version et la gestion du code source.
- ## Dépendances

  - 🧩 **django** : Framework web principal.
  - 🐼 **pandas** : Manipulation et analyse des données.
  - 🔢 **numpy** : Calculs numériques avancés.
  - 🤖 **scikit-learn** : Modèles de machine learning.
  - 🗃️ **joblib** : Sérialisation des modèles ML.
  - 🗣️ **textblob** : Traitement du langage naturel.
  - 🌍 **requests** : Requêtes HTTP pour communiquer avec des APIs externes.
  - 🐿️ **gunicorn** : Serveur WSGI pour déployer des applications Python.

- **Ressources** :
  - 🖼️ Font Awesome (CDN) : Bibliothèque d'icônes pour améliorer l'interface utilisateur.
  - 📍 API Nominatim (géolocalisation) : Service de géolocalisation pour obtenir les coordonnées des donneurs.

## Installation 🛠️

1. **Cloner le projet** :
   - Utilisez la commande suivante pour cloner le dépôt : `git clone <URL>`
   - Ou bien, téléchargez et décompressez le dossier contenant le code source.

2. **Créer un environnement virtuel** :
   - Exécutez la commande : `python -m venv venv`
   - Activez l'environnement virtuel (Windows) : `venv\Scripts\activate`

3. **Installer les dépendances** :
   - Installez les paquets nécessaires avec : `pip install -r requirements.txt`

4. **Configurer les paramètres** :
   - Modifiez le fichier `settings.py` pour définir `DEBUG=True` et utilisez SQLite par défaut.

5. **Appliquer les migrations** :
   - Créez et appliquez les migrations de base de données avec : `python manage.py makemigrations && python manage.py migrate`

6. **Créer un superutilisateur** :
   - Créez un compte administrateur avec : `python manage.py createsuperuser`

7. **Ajouter le modèle de Machine Learning** :
   - Placez le fichier `eligibility_model.pkl` dans le répertoire `campagne/ml/`

8. **Lancer le serveur** :
   - Démarrez le serveur de développement avec : `python manage.py runserver`
   - Accédez à l'application via : `http://127.0.0.1:8000/`

## Structure 📁

- `campagne/` : Modèles, vues, templates (ex. `donors.html`, `prediction.html`), ML (`eligibility_model.pkl`).
- `DonDeSang/` : Configuration Django (`settings.py`, `urls.py`).
- `static/` : CSS/JS/Images.
- `manage.py`, `db.sqlite3`, `README.md`.

## Fonctionnalités 🚀

- **Liste des donneurs** : `/donors/`  
  📝 Affiche la liste complète des donneurs avec des options pour créer, lire, mettre à jour et supprimer (CRUD) les entrées.

- **Ajout/Modification** :  
  🌍 Formulaires interactifs permettant d'ajouter ou de modifier les informations des donneurs avec une fonctionnalité de géolocalisation intégrée.

- **Prédiction** : `/prediction/`  
  🤖 Utilisez le machine learning pour prédire l'éligibilité des donneurs directement sur cette page.

## Design 🎨

- **Couleurs** :
  - Rouge (#B22222) pour les accents et les éléments importants.
  - Gris (#F8F9FA) pour les arrière-plans neutres.
  - Texte sombre (#333333) pour une meilleure lisibilité.

- **Responsive** :
  - 📱 Interface adaptable à toutes les tailles d'écran, utilisant des grilles flexibles et des transitions fluides pour une expérience utilisateur optimale.

## Déploiement 🚀

- **Configuration de production** :
  - `DEBUG=False` : Désactive le mode debug pour la production.
  - `ALLOWED_HOSTS` : Spécifiez les hôtes autorisés à accéder à l'application.
  - **Base de données** : Utilisez PostgreSQL pour la base de données en production.
  - **Static files** : Exécutez `collectstatic` pour collecter les fichiers statiques.
  - **Serveur d'application** : Utilisez Gunicorn pour servir l'application.
  - **Serveur web** : Configurez Nginx comme serveur web en frontal.

## Contribution 🤝

- **Processus de contribution** :
  - Forkez le dépôt.
  - Créez une nouvelle branche pour votre fonctionnalité ou correctif : `git checkout -b feature/<nom>`.
  - Soumettez une pull request pour révision.

## Licence 📄

- **Type de licence** : MIT (à confirmer).  
  Cela signifie que vous pouvez utiliser, copier, modifier, fusionner, publier, distribuer, sous-licencier et/ou vendre des copies de ce logiciel.

## Crédits 🙏

- **Développeur** : CodeStorm team
- **Assistance** : Grok (xAI)  
  Merci à toutes les personnes qui ont contribué à ce projet.
