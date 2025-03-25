from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('geo/', views.geo, name='geo'),
    path('health/', views.health, name='health'),
    path('profiling/', views.profiling, name='profiling'),
    path('efficiency/', views.efficiency, name='efficiency'),
    path('loyalty/', views.loyalty, name='loyalty'),
    path('sentiment/', views.sentiment, name='sentiment'),
    path('prediction/', views.prediction, name='prediction'),
    path('add_donor/', views.add_donor, name='add_donor'),
    path('donors/', views.donors, name='donors'),
    path('donors/delete/<int:donor_id>/', views.delete_donor, name='delete_donor'),
    path('donors/update/<int:donor_id>/', views.update_donor, name='update_donor'),
    path('api/predict_eligibility/', views.predict_eligibility_api, name='predict_eligibility_api'),
]