# Projet Don de Sang

## Aperçu
Application web Django pour gérer une base de données de donneurs de sang. Elle centralise les informations (âge, genre, profession, localisation, santé, dons), prédit l’éligibilité via un modèle machine learning, et fournit des analyses statistiques. Interface moderne et responsive (palette rouge/grise, icônes Font Awesome).

## Objectifs
- Gérer les données des donneurs.
- Prédire l’éligibilité avec ML.
- Interface intuitive pour CRUD (ajouter, modifier, supprimer, analyser).
- Géolocalisation automatique.

## Prérequis
- **Framework web** : Django 4.2.16
- **Logiciels** : Python 3.9.6+, navigateur web, Git (optionnel).
- **Dépendances** : `django`, `pandas`, `numpy`, `scikit-learn`, `joblib`, `textblob`, `requests`.
- **Ressources** : Font Awesome (CDN), API Nominatim (géolocalisation).

## Installation
1. Cloner : `git clone <URL>` ou alors télécharger et  décompresser le dossier contenant le code source.
2. Environnement virtuel : `python -m venv venv` puis `venv\Scripts\activate` (Windows).
3. Dépendances : `pip install -r requirements.txt`.
4. Configurer `settings.py` (DEBUG=True, SQLite par défaut).
5. Migrations : `python manage.py makemigrations && python manage.py migrate`.
6. Superutilisateur : `python manage.py createsuperuser`.
7. Modèle ML : Placer `eligibility_model.pkl` dans `campagne/ml/`.
8. Lancer : `python manage.py runserver` (accès : `http://127.0.0.1:8000/`).

## Structure
- `campagne/` : Modèles, vues, templates (ex. `donors.html`, `prediction.html`), ML (`eligibility_model.pkl`).
- `DonDeSang/` : Configuration Django (`settings.py`, `urls.py`).
- `static/` : CSS/JS/Images.
- `manage.py`, `db.sqlite3`, `README.md`.

## Fonctionnalités
- **Liste des donneurs** : `/donors/` (affichage, CRUD).
- **Ajout/Modification** : Formulaires avec géolocalisation.
- **Prédiction** : Éligibilité via ML sur `/prediction/`.

## Design
- Couleurs : Rouge (#B22222), gris (#F8F9FA), texte sombre (#333333).
- Responsive, avec grilles et transitions.

## Déploiement
- `DEBUG=False`, `ALLOWED_HOSTS`, PostgreSQL, `collectstatic`, Gunicorn, Nginx.

## Contribution
Fork, branche (`git checkout -b feature/<nom>`), pull request.

## Licence
MIT (à confirmer).

## Crédits
Développeur : CodeStorm. Assistance : Grok (xAI).