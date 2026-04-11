from django.db import models

# Create your models here.

class Product(models.Model):
    id_on_store = models.CharField(max_length=16)
    name = models.CharField(max_length=256)
    popularity = models.IntegerField()
    img = models.URLField()
    details = models.TextField(max_length=1024)
    description = models.TextField(max_length=2048)
    created = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class PriceLog(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    nameOnStore = models.CharField(max_length=256)
    price = models.FloatField()
    store = models.CharField(max_length=64)
    relocate = models.URLField()
    delivery_time = models.CharField(max_length=128)
    delivery_details = models.TextField(max_length=1024)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.nameOnStore} on {self.store}"