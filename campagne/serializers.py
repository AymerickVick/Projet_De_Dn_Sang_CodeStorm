from rest_framework import serializers

class PredictionSerializer(serializers.Serializer):
    age = serializers.IntegerField()
    genre = serializers.CharField(max_length=10)
    profession = serializers.CharField(max_length=100)
    quartier = serializers.CharField(max_length=100)
    hypertension = serializers.BooleanField()
    diabete = serializers.BooleanField()
    asthme = serializers.BooleanField()
    hiv_hbs_hcv = serializers.BooleanField()
    tatoue = serializers.BooleanField()