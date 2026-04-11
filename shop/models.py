from django.db import models
from authentication.models import CustomUser
# Create your models here.

class Product(models.Model):
    name = models.CharField(max_length=128)
    price = models.FloatField()
    image = models.URLField()
    stock = models.IntegerField()
    description = models.TextField(max_length=1024)
    created = models.DateTimeField(auto_now_add=True)

class Order(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    price = models.FloatField()
    quantity = models.IntegerField()
    payement_id = models.CharField(max_length=128, null=True)
    payement_reference = models.CharField(max_length=128, null=True)
    status = models.CharField(max_length=128)
    created = models.DateTimeField(auto_now_add=True)
