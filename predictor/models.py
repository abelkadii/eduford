from django.db import models
from authentication.models import CustomUser
import datetime
# Create your models here.

class Diagnosis(models.Model):
    # user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    symptoms = models.TextField(max_length=4096)
    name = models.CharField(max_length=128)
    age = models.FloatField()
    weight = models.FloatField()
    height = models.FloatField()
    gender = models.CharField(max_length=128)
    cigar = models.CharField(max_length=128, null=True)
    alcohol = models.CharField(max_length=128, null=True)
    pregnant = models.CharField(max_length=128, null=True)
    trimister = models.CharField(max_length=128, null=True)
    uuid = models.CharField(max_length=32)
    created = models.DateTimeField(auto_now_add=True)