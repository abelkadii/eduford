from django.db import models
from authentication.models import CustomUser
# Create your models here.

class Location(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    lat = models.FloatField()
    lng = models.FloatField()
    country = models.CharField(max_length=128)
    address = models.CharField(max_length=128)
