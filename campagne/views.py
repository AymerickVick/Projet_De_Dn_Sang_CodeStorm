from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django import forms
from .models import Donor
from django.db.models import Count, Avg
from django.db.models import Count
from datetime import datetime
import json
import numpy as np
from sklearn.cluster import KMeans
from django.db import models
from django.contrib import messages
from textblob import TextBlob
from django.db.models.functions import ExtractMonth, ExtractYear
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Donor
from django.db.models import Avg
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import PredictionSerializer
import joblib
from sklearn.preprocessing import LabelEncoder
import pandas as pd



# Charger le modèle et initialiser les encodeurs
model = joblib.load('campagne/ml/eligibility_model.pkl')

# Initialisation des encodeurs
le_genre = LabelEncoder()
le_profession = LabelEncoder()
le_quartier = LabelEncoder()

# Entraîner les encodeurs avec des données par défaut ou dynamiques
def initialize_encoders():
    # Récupérer les données depuis la base de données
    donors = Donor.objects.all()
    
    # Genres possibles
    genres = list(set(donor.genre for donor in donors if donor.genre)) + ['Inconnu']
    le_genre.fit(genres if genres else ['Homme', 'Femme', 'Autre', 'Inconnu'])
    
    # Professions possibles
    professions = list(set(donor.profession for donor in donors if donor.profession)) + ['Inconnu']
    le_profession.fit(professions if professions else ['Inconnu'])
    
    # Quartiers possibles
    quartiers = list(set(donor.quartier for donor in donors if donor.quartier)) + ['Inconnu']
    le_quartier.fit(quartiers if quartiers else ['Inconnu'])

# Appeler l'initialisation au démarrage
initialize_encoders()

# Fonction pour vérifier l’éligibilité manuellement
def check_eligibility_manually(data):
    return not (data['hypertension'] or data['diabete'] or data['asthme'] or 
                data['hiv_hbs_hcv'] or data['tatoue'] or data['age'] < 18 or data['age'] > 65)

class DonorForm(forms.ModelForm):
    class Meta:
        model = Donor
        fields = '__all__'
        widgets = {
            'date_remplissage': forms.DateInput(attrs={'type': 'date'}),
            'date_naissance': forms.DateInput(attrs={'type': 'date'}),
        }

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
    return render(request, 'login.html', {'form': forms.Form()})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard(request):
    total_donors = Donor.objects.count()
    donors = Donor.objects.all()
    if total_donors > 0:
        # Calcul de l’âge moyen avec une gestion des cas où age() pourrait échouer
        try:
            avg_age = sum(donor.age() for donor in donors) / total_donors
        except (AttributeError, TypeError):
            # Si Donor.age() n’existe pas, calcul manuel avec date_naissance
            avg_age = sum(
                (2025 - donor.date_naissance.year) if donor.date_naissance else 0
                for donor in donors
            ) / total_donors
    else:
        avg_age = 0
    return render(request, 'dashboard.html', {
        'total_donors': total_donors,
        'avg_age': round(avg_age, 1)
    })

@login_required
def geo(request):
    donors_map = Donor.objects.values('arrondissement', 'quartier') \
                              .annotate(
                                  count=Count('id'),
                                  avg_latitude=Avg('latitude'),
                                  avg_longitude=Avg('longitude')
                              ) \
                              .filter(avg_latitude__isnull=False, avg_longitude__isnull=False)

    donors_map_data = [
        {
            'arrondissement': donor['arrondissement'],
            'quartier': donor['quartier'],
            'count': donor['count'],
            'latitude': donor['avg_latitude'],
            'longitude': donor['avg_longitude']
        }
        for donor in donors_map
    ]

    donors_graph = Donor.objects.values('arrondissement') \
                                .annotate(count=Count('id')) \
                                .order_by('arrondissement')

    donors_graph_data = {
        'labels': [donor['arrondissement'] for donor in donors_graph],
        'counts': [donor['count'] for donor in donors_graph]
    }

    return render(request, 'geo.html', {
        'donors_json': json.dumps(donors_map_data),
        'graph_json': json.dumps(donors_graph_data)
    })

@login_required
def health(request):
    total = Donor.objects.count()

    # Compter les donneurs par condition
    health_stats = {
        'hypertension': {
            'count': Donor.objects.filter(hypertension=True).count(),
            'percentage': (Donor.objects.filter(hypertension=True).count() / total * 100) if total > 0 else 0
        },
        'diabete': {
            'count': Donor.objects.filter(diabete=True).count(),
            'percentage': (Donor.objects.filter(diabete=True).count() / total * 100) if total > 0 else 0
        },
        'asthme': {
            'count': Donor.objects.filter(asthme=True).count(),
            'percentage': (Donor.objects.filter(asthme=True).count() / total * 100) if total > 0 else 0
        },
        'hiv_hbs_hcv': {
            'count': Donor.objects.filter(hiv_hbs_hcv=True).count(),
            'percentage': (Donor.objects.filter(hiv_hbs_hcv=True).count() / total * 100) if total > 0 else 0
        },
        'tatoue': {
            'count': Donor.objects.filter(tatoue=True).count(),
            'percentage': (Donor.objects.filter(tatoue=True).count() / total * 100) if total > 0 else 0
        },
        'total': total,
    }

    # Éligibilité : Non éligible si au moins une condition est True
    eligible = Donor.objects.filter(
        hypertension=False,
        diabete=False,
        asthme=False,
        hiv_hbs_hcv=False,
        tatoue=False
    ).count()
    non_eligible = total - eligible

    eligibility_stats = {
        'eligible': eligible,
        'non_eligible': non_eligible,
    }

    return render(request, 'health.html', {
        'health_stats': health_stats,
        'eligibility_stats': json.dumps(eligibility_stats)
    })
    
@login_required
def profiling(request):
    # Distribution par genre
    gender_dist = Donor.objects.values('genre').annotate(count=Count('genre'))

    # Distribution par âge
    donors = Donor.objects.all()
    today = datetime.now().date()
    age_groups = {'0_18': 0, '19_30': 0, '31_50': 0, '51_plus': 0}
    for donor in donors:
        age = donor.age()
        if age <= 18:
            age_groups['0_18'] += 1
        elif 19 <= age <= 30:
            age_groups['19_30'] += 1
        elif 31 <= age <= 50:
            age_groups['31_50'] += 1
        else:
            age_groups['51_plus'] += 1

    # Préparation des données pour le clustering
    donor_data = []
    for donor in donors:
        donor_data.append([
            donor.age(),                         # Âge
            1 if donor.genre == 'Homme' else 0,  # Genre (1 = Homme, 0 = Femme)
            1 if donor.hypertension else 0,      # Hypertension
            1 if donor.diabete else 0,           # Diabète
            1 if donor.asthme else 0,            # Asthme
            1 if donor.hiv_hbs_hcv else 0,       # HIV/HBS/HCV
            1 if donor.tatoue else 0             # Tatoué
        ])

    # Si pas de donneurs, éviter le clustering
    if not donor_data:
        clusters = []
        cluster_insights = {}
    else:
        # Clustering avec K-means (3 clusters par défaut)
        kmeans = KMeans(n_clusters=3, random_state=42)
        cluster_labels = kmeans.fit_predict(donor_data)

        # Ajouter les labels aux donneurs
        for i, donor in enumerate(donors):
            donor.cluster = cluster_labels[i]

        # Générer des insights par cluster
        cluster_insights = {}
        for cluster_id in range(3):
            cluster_donors = [d for i, d in enumerate(donors) if cluster_labels[i] == cluster_id]
            if cluster_donors:
                total = len(cluster_donors)
                avg_age = np.mean([d.age() for d in cluster_donors])
                male_pct = sum(1 for d in cluster_donors if d.genre == 'Homme') / total * 100
                eligible = sum(1 for d in cluster_donors if not (d.hypertension or d.diabete or d.asthme or d.hiv_hbs_hcv or d.tatoue)) / total * 100
                cluster_insights[cluster_id] = {
                    'count': total,
                    'avg_age': avg_age,
                    'male_pct': male_pct,
                    'eligible_pct': eligible,
                }

    # Préparer les données pour le graphique
    cluster_data = {
        'labels': [f'Cluster {i}' for i in cluster_insights.keys()],
        'counts': [cluster_insights[i]['count'] for i in cluster_insights.keys()],
        'avg_ages': [cluster_insights[i]['avg_age'] for i in cluster_insights.keys()],
        'eligible_pcts': [cluster_insights[i]['eligible_pct'] for i in cluster_insights.keys()],
    }

    return render(request, 'profiling.html', {
        'gender_dist': gender_dist,
        'age_groups': age_groups,
        'cluster_insights': cluster_insights,
        'cluster_data': json.dumps(cluster_data),
    })
    
@login_required
def efficiency(request):
    # Moyenne des dons par donneur
    avg_dons = Donor.objects.aggregate(Avg('nombre_dons'))['nombre_dons__avg'] or 0

    # Analyse par mois (tendance temporelle)
    dons_par_mois = Donor.objects.annotate(
        month=models.functions.ExtractMonth('date_remplissage')  # Utilisation correcte avec import
    ).values('month').annotate(count=Count('id')).order_by('month')

    mois_labels = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin', 'Juil', 'Août', 'Sep', 'Oct', 'Nov', 'Déc']
    dons_mensuels = {i+1: 0 for i in range(12)}  # Initialiser tous les mois à 0
    for entry in dons_par_mois:
        dons_mensuels[entry['month']] = entry['count']
    
    # Mois avec le plus de dons
    max_mois = max(dons_mensuels.items(), key=lambda x: x[1], default=(None, 0))
    mois_plus_eleve = mois_labels[max_mois[0] - 1] if max_mois[0] else "Aucun"

    # Répartition par genre
    genre_dist = Donor.objects.values('genre').annotate(count=Count('id'))
    genre_data = {
        'labels': [g['genre'] for g in genre_dist],
        'counts': [g['count'] for g in genre_dist],
    }

    # Répartition par tranche d’âge
    donors = Donor.objects.all()
    age_groups = {'0_18': 0, '19_30': 0, '31_50': 0, '51_plus': 0}
    for donor in donors:
        age = donor.age()
        if age <= 18:
            age_groups['0_18'] += 1
        elif 19 <= age <= 30:
            age_groups['19_30'] += 1
        elif 31 <= age <= 50:
            age_groups['31_50'] += 1
        else:
            age_groups['51_plus'] += 1

    # Groupe démographique dominant (par âge et genre)
    dominant_group = max(age_groups.items(), key=lambda x: x[1], default=('Aucun', 0))

    # Préparer les données pour les graphiques
    chart_data = {
        'mois': {
            'labels': mois_labels,
            'counts': [dons_mensuels[i+1] for i in range(12)],
        },
        'genre': genre_data,
        'age': {
            'labels': ['0-18', '19-30', '31-50', '51+'],
            'counts': [age_groups['0_18'], age_groups['19_30'], age_groups['31_50'], age_groups['51_plus']],
        },
    }

    context = {
        'avg_dons': round(avg_dons, 2),
        'mois_plus_eleve': mois_plus_eleve,
        'dominant_group': dominant_group[0],
        'chart_data': json.dumps(chart_data),
    }
    return render(request, 'efficiency.html', context)

@login_required
def loyalty(request):
    # Nombre de donneurs ayant donné 2 fois ou plus
    loyal_donors = Donor.objects.values('user_id').annotate(donation_count=Count('id')).filter(donation_count__gte=2).count()
    # Nombre total de donneurs uniques
    total_donors = Donor.objects.values('user_id').distinct().count()
    # Pourcentage de fidélité
    percentage = (loyal_donors / total_donors * 100) if total_donors > 0 else 0

    # Statistiques supplémentaires
    avg_donations = Donor.objects.values('user_id').annotate(donation_count=Count('id')).aggregate(Avg('donation_count'))['donation_count__avg'] or 0

    # Distribution par nombre de dons
    donation_dist = Donor.objects.values('user_id').annotate(donation_count=Count('id')).values('donation_count').annotate(count=Count('user_id')).order_by('donation_count')
    donation_labels = [entry['donation_count'] for entry in donation_dist]
    donation_counts = [entry['count'] for entry in donation_dist]

    # Analyse démographique des donneurs fidèles
    loyal_users = Donor.objects.values('user_id').annotate(donation_count=Count('id')).filter(donation_count__gte=2).values_list('user_id', flat=True)
    loyal_donors_data = Donor.objects.filter(user_id__in=loyal_users)

    # Par âge
    age_groups = {'0_18': 0, '19_30': 0, '31_50': 0, '51_plus': 0}
    for donor in loyal_donors_data:
        age = donor.age()
        if age <= 18:
            age_groups['0_18'] += 1
        elif 19 <= age <= 30:
            age_groups['19_30'] += 1
        elif 31 <= age <= 50:
            age_groups['31_50'] += 1
        else:
            age_groups['51_plus'] += 1

    # Par genre
    gender_dist = loyal_donors_data.values('genre').annotate(count=Count('id'))

    # Par profession (top 5)
    profession_dist = loyal_donors_data.values('profession').annotate(count=Count('id')).order_by('-count')[:5]

    # Par région (quartier, top 5)
    region_dist = loyal_donors_data.values('quartier').annotate(count=Count('id')).order_by('-count')[:5]

    # Données pour les graphiques
    chart_data = {
        'donation_dist': {
            'labels': donation_labels,
            'counts': donation_counts
        },
        'age_dist': {
            'labels': ['0-18', '19-30', '31-50', '51+'],
            'counts': [age_groups['0_18'], age_groups['19_30'], age_groups['31_50'], age_groups['51_plus']]
        },
        'gender_dist': {
            'labels': [g['genre'] for g in gender_dist],
            'counts': [g['count'] for g in gender_dist]
        }
    }

    context = {
        'loyal_donors': loyal_donors,
        'total_donors': total_donors,
        'percentage': percentage,
        'avg_donations': avg_donations,
        'donation_dist': donation_dist,
        'age_groups': age_groups,
        'gender_dist': gender_dist,
        'profession_dist': profession_dist,
        'region_dist': region_dist,
        'chart_data': json.dumps(chart_data)
    }
    return render(request, 'loyalty.html', context)

@login_required
def sentiment(request):
    # Récupérer les feedbacks non nuls
    feedback_data = Donor.objects.filter(feedback__isnull=False).values('feedback', 'date_remplissage', 'genre', 'quartier', 'date_naissance')

    # Analyse de sentiment
    sentiment_counts = {'positif': 0, 'negatif': 0, 'neutre': 0}
    feedback_list = []
    for entry in feedback_data:
        feedback = entry['feedback']
        blob = TextBlob(feedback)
        polarity = blob.sentiment.polarity  # -1 (négatif) à 1 (positif)
        if polarity > 0:
            sentiment = 'positif'
        elif polarity < 0:
            sentiment = 'negatif'
        else:
            sentiment = 'neutre'
        sentiment_counts[sentiment] += 1
        feedback_list.append({
            'text': feedback,
            'sentiment': sentiment,
            'date': entry['date_remplissage'],
            'genre': entry['genre'],
            'quartier': entry['quartier'],
            'age': (entry['date_remplissage'].year - entry['date_naissance'].year) if entry['date_naissance'] else None
        })

    # Tendances temporelles (par mois)
    monthly_sentiment = Donor.objects.filter(feedback__isnull=False).annotate(
        year=ExtractYear('date_remplissage'),
        month=ExtractMonth('date_remplissage')
    ).values('year', 'month').annotate(
        count=Count('id')
    ).order_by('year', 'month')
    time_labels = [f"{entry['year']}-{entry['month']:02d}" for entry in monthly_sentiment]
    time_counts = [entry['count'] for entry in monthly_sentiment]

    # Sentiment par groupe démographique
    # Par genre
    gender_sentiment = {}
    for entry in feedback_list:
        genre = entry['genre']
        if genre not in gender_sentiment:
            gender_sentiment[genre] = {'positif': 0, 'negatif': 0, 'neutre': 0}
        gender_sentiment[genre][entry['sentiment']] += 1

    # Par âge
    age_sentiment = {'0_18': {'positif': 0, 'negatif': 0, 'neutre': 0},
                     '19_30': {'positif': 0, 'negatif': 0, 'neutre': 0},
                     '31_50': {'positif': 0, 'negatif': 0, 'neutre': 0},
                     '51_plus': {'positif': 0, 'negatif': 0, 'neutre': 0}}
    for entry in feedback_list:
        if entry['age']:
            if entry['age'] <= 18:
                age_sentiment['0_18'][entry['sentiment']] += 1
            elif 19 <= entry['age'] <= 30:
                age_sentiment['19_30'][entry['sentiment']] += 1
            elif 31 <= entry['age'] <= 50:
                age_sentiment['31_50'][entry['sentiment']] += 1
            else:
                age_sentiment['51_plus'][entry['sentiment']] += 1

    # Données pour graphiques
    chart_data = {
        'sentiment_dist': {
            'labels': ['Positif', 'Négatif', 'Neutre'],
            'counts': [sentiment_counts['positif'], sentiment_counts['negatif'], sentiment_counts['neutre']]
        },
        'time_dist': {
            'labels': time_labels,
            'counts': time_counts
        },
        'gender_dist': {
            'labels': list(gender_sentiment.keys()),
            'positif': [gender_sentiment[g]['positif'] for g in gender_sentiment],
            'negatif': [gender_sentiment[g]['negatif'] for g in gender_sentiment],
            'neutre': [gender_sentiment[g]['neutre'] for g in gender_sentiment]
        },
        'age_dist': {
            'labels': ['0-18', '19-30', '31-50', '51+'],
            'positif': [age_sentiment[key]['positif'] for key in age_sentiment],
            'negatif': [age_sentiment[key]['negatif'] for key in age_sentiment],
            'neutre': [age_sentiment[key]['neutre'] for key in age_sentiment]
        }
    }

    context = {
        'feedback_list': feedback_list,
        'sentiment_counts': sentiment_counts,
        'chart_data': json.dumps(chart_data)
    }
    return render(request, 'sentiment.html', context)

@login_required
def prediction(request):
    # Calculs initiaux
    avg_dons = Donor.objects.aggregate(Avg('nombre_dons'))['nombre_dons__avg'] or 0
    predicted_dons = round(avg_dons * Donor.objects.count() * 1.1)
    quartiers = Donor.objects.values_list('quartier', flat=True).distinct()
    donneurs = Donor.objects.all()

    # Formulaire pour un nouveau donneur
    if request.method == 'POST' and 'new_donor_submit' in request.POST:
        data = {
            'age': int(request.POST.get('age', 0)),
            'genre': request.POST.get('genre', 'Inconnu'),
            'profession': request.POST.get('profession', 'Inconnu'),  # Accepte n'importe quoi
            'quartier': 'Inconnu',  # Automatique
            'hypertension': request.POST.get('hypertension') == 'on',
            'diabete': request.POST.get('diabete') == 'on',
            'asthme': request.POST.get('asthme') == 'on',
            'hiv_hbs_hcv': request.POST.get('hiv_hbs_hcv') == 'on',
            'tatoue': request.POST.get('tatoue') == 'on',
        }
        df = pd.DataFrame([data])

        # Encoder les variables
        df['genre'] = le_genre.transform([df['genre'][0]])[0]
        
        # Gestion de la profession : si inconnue, utiliser 'Inconnu'
        if df['profession'][0] not in le_profession.classes_:
            df['profession'] = le_profession.transform(['Inconnu'])[0]
        else:
            df['profession'] = le_profession.transform([df['profession'][0]])[0]

        # Quartier (automatique)
        if df['quartier'][0] not in le_quartier.classes_:
            df['quartier'] = le_quartier.transform(['Inconnu'])[0]
        else:
            df['quartier'] = le_quartier.transform([df['quartier'][0]])[0]

        # Prédiction
        ml_prediction = model.predict(df)[0]
        manual_eligibility = check_eligibility_manually(data)
        result = {
            'ml': 'Éligible' if ml_prediction == 1 else 'Non éligible',
            'manual': 'Éligible' if manual_eligibility else 'Non éligible'
        }
        return render(request, 'prediction.html', {
            'predicted_dons': predicted_dons,
            'prediction_result': result,
            'input_data': data,
            'quartiers': quartiers,
            'donneurs': donneurs
        })

    # Formulaire pour un donneur existant
    if request.method == 'POST' and 'existing_donor_submit' in request.POST:
        donor_id = request.POST.get('donor_id')
        try:
            donor = Donor.objects.get(id=donor_id)
            data = {
                'age': donor.age() if hasattr(donor, 'age') else (donor.date_remplissage.year - donor.date_naissance.year) if donor.date_naissance else 0,
                'genre': donor.genre or 'Inconnu',
                'profession': donor.profession or 'Inconnu',
                'quartier': donor.quartier or 'Inconnu',
                'hypertension': donor.hypertension if donor.hypertension is not None else False,
                'diabete': donor.diabete if donor.diabete is not None else False,
                'asthme': donor.asthme if donor.asthme is not None else False,
                'hiv_hbs_hcv': donor.hiv_hbs_hcv if donor.hiv_hbs_hcv is not None else False,
                'tatoue': donor.tatoue if donor.tatoue is not None else False,
            }
            df = pd.DataFrame([data])

            # Encoder les variables
            df['genre'] = le_genre.transform([df['genre'][0]])[0]
            
            # Gestion de la profession
            if df['profession'][0] not in le_profession.classes_:
                df['profession'] = le_profession.transform(['Inconnu'])[0]
            else:
                df['profession'] = le_profession.transform([df['profession'][0]])[0]

            # Gestion du quartier
            if df['quartier'][0] not in le_quartier.classes_:
                df['quartier'] = le_quartier.transform(['Inconnu'])[0]
            else:
                df['quartier'] = le_quartier.transform([df['quartier'][0]])[0]

            # Prédiction
            ml_prediction = model.predict(df)[0]
            manual_eligibility = check_eligibility_manually(data)
            result = {
                'ml': 'Éligible' if ml_prediction == 1 else 'Non éligible',
                'manual': 'Éligible' if manual_eligibility else 'Non éligible'
            }
            return render(request, 'prediction.html', {
                'predicted_dons': predicted_dons,
                'prediction_result': result,
                'selected_donor': donor,
                'quartiers': quartiers,
                'donneurs': donneurs
            })
        except Donor.DoesNotExist:
            return render(request, 'prediction.html', {
                'predicted_dons': predicted_dons,
                'error': 'Donneur non trouvé',
                'quartiers': quartiers,
                'donneurs': donneurs
            })

    return render(request, 'prediction.html', {
        'predicted_dons': predicted_dons,
        'quartiers': quartiers,
        'donneurs': donneurs
    })

@api_view(['POST'])
def predict_eligibility_api(request):
    serializer = PredictionSerializer(data=request.data)
    if serializer.is_valid():
        data = serializer.validated_data
        df = pd.DataFrame([data])
        df['genre'] = le_genre.transform([df['genre'][0]])[0]
        df['profession'] = le_profession.transform([df['profession'][0] if df['profession'][0] in professions else 'Inconnu'])[0]
        df['quartier'] = le_quartier.transform([df['quartier'][0] if df['quartier'][0] in quartiers else 'Inconnu'])[0]
        prediction = model.predict(df)[0]
        return Response({'eligible': bool(prediction)})
    return Response(serializer.errors, status=400)

@login_required
def add_donor(request):
    if request.method == 'POST':
        donor = Donor(
            user=request.user,
            date_naissance=request.POST['date_naissance'],
            genre=request.POST['genre'],
            profession=request.POST['profession'],
            arrondissement=request.POST['arrondissement'],
            quartier=request.POST['quartier'],
            hypertension='hypertension' in request.POST,
            diabete='diabete' in request.POST,
            asthme='asthme' in request.POST,
            hiv_hbs_hcv='hiv_hbs_hcv' in request.POST,
            tatoue='tatoue' in request.POST,
            feedback=request.POST.get('feedback', ''),
            nombre_dons=int(request.POST['nombre_dons']),
            # Ajouter latitude et longitude si vous voulez les stocker
            # latitude=float(request.POST.get('latitude', 0)) si ajouté au formulaire
            # longitude=float(request.POST.get('longitude', 0)) si ajouté au formulaire
        )
        donor.save()
        return redirect('dashboard')
    return render(request, 'add_donor.html')

@login_required
def donors(request):
    donor_list = Donor.objects.all()
    print("Nombre de donneurs:", donor_list.count())  # Debug
    return render(request, 'donors.html', {'donor_list': donor_list})

@login_required
def delete_donor(request, donor_id):
    donor = get_object_or_404(Donor, id=donor_id)
    if request.method == 'POST':
        donor.delete()
        messages.success(request, f"Donneur {donor_id} supprimé avec succès.")
        return redirect('donors')
    return render(request, 'confirm_delete.html', {'donor': donor})

@login_required
def update_donor(request, donor_id):
    donor = get_object_or_404(Donor, id=donor_id)
    if request.method == 'POST':
        donor.date_naissance = request.POST.get('date_naissance', donor.date_naissance)
        donor.genre = request.POST.get('genre', donor.genre)
        donor.profession = request.POST.get('profession', donor.profession)
        donor.arrondissement = request.POST.get('arrondissement', donor.arrondissement)
        donor.quartier = request.POST.get('quartier', donor.quartier)
        donor.hypertension = 'hypertension' in request.POST
        donor.diabete = 'diabete' in request.POST
        donor.asthme = 'asthme' in request.POST
        donor.hiv_hbs_hcv = 'hiv_hbs_hcv' in request.POST
        donor.tatoue = 'tatoue' in request.POST
        donor.feedback = request.POST.get('feedback', donor.feedback)
        donor.nombre_dons = int(request.POST.get('nombre_dons', donor.nombre_dons))
        donor.save()
        messages.success(request, f"Donneur {donor_id} mis à jour avec succès.")
        return redirect('donors')
    return render(request, 'update_donor.html', {'donor': donor})