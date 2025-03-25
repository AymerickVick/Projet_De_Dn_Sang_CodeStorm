import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import joblib
from campagne.models import Donor

# Récupérer les données
data = Donor.objects.all().values('date_naissance', 'genre', 'profession', 'quartier', 
                                  'hypertension', 'diabete', 'asthme', 'hiv_hbs_hcv', 'tatoue')

# Convertir en DataFrame
df = pd.DataFrame(list(data))

# Calculer l’âge
df['age'] = df['date_naissance'].apply(lambda x: 2025 - x.year if x else 0)
df = df.drop(columns=['date_naissance'])

# Encoder les variables catégoriques avec 'Inconnu' pour les valeurs nulles
le = LabelEncoder()
for col in ['genre', 'profession', 'quartier']:
    df[col] = df[col].fillna('Inconnu')
    le.fit(list(df[col].unique()) + ['Inconnu'])  # Ajouter 'Inconnu' au vocabulaire
    df[col] = le.transform(df[col])

# Définir l’éligibilité (pas de conditions de santé graves)
df['eligible'] = (~df[['hypertension', 'diabete', 'asthme', 'hiv_hbs_hcv']].any(axis=1)).astype(int)

# Features et cible
X = df[['age', 'genre', 'profession', 'quartier', 'hypertension', 'diabete', 'asthme', 'hiv_hbs_hcv', 'tatoue']]
y = df['eligible']

# Séparer les données
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Entraîner le modèle
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Sauvegarder le modèle
joblib.dump(model, 'campagne/ml/eligibility_model.pkl')

# Évaluer le modèle
accuracy = model.score(X_test, y_test)
print(f"Précision du modèle : {accuracy:.2f}")