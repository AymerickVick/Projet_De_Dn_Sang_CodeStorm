from django.db import models
from django.contrib.auth.models import User
from datetime import datetime

class Donor(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    date_naissance = models.DateField()
    date_remplissage = models.DateField(auto_now_add=True)  # Date auto-remplie à la création
    genre = models.CharField(
        max_length=10,
        choices=[('Homme', 'Homme'), ('Femme', 'Femme')],
        default='Homme'
    )
    profession = models.CharField(max_length=100)
    arrondissement = models.CharField(max_length=100)
    quartier = models.CharField(max_length=100)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    asthme = models.BooleanField(default=False)
    diabete = models.BooleanField(default=False)
    hypertension = models.BooleanField(default=False)
    hiv_hbs_hcv = models.BooleanField(default=False)
    tatoue = models.BooleanField(default=False)
    nombre_dons = models.IntegerField(default=0)
    feedback = models.TextField(null=True, blank=True)

    def age(self):
        """Calcule l’âge exact en années à partir de date_naissance et date_remplissage."""
        today = self.date_remplissage  # Utilise date_remplissage comme référence
        age = today.year - self.date_naissance.year - (
            (today.month, today.day) < (self.date_naissance.month, self.date_naissance.day)
        )
        return age

    def __str__(self):
        """Représentation textuelle du donneur."""
        username = self.user.username if self.user else 'Anonyme'
        return f"Donneur {self.id} - {username} ({self.profession}, {self.quartier})"

    class Meta:
        verbose_name = "Donneur"
        verbose_name_plural = "Donneurs"