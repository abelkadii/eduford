from django.db import models
from authentication.models import CustomUser
# Create your models here.


class Appointment(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100, default="")
    last_name = models.CharField(max_length=100, default="")
    payement_id = models.CharField(max_length=128, null=True)
    payement_reference = models.CharField(max_length=128, null=True)
    status = models.CharField(max_length=128, null=True)
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    date = models.DateField()
    time = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} booked an appointment on {self.date} {self.time}"
    def __repr__(self):
        return f"{self.first_name} {self.last_name} booked an appointment on {self.date} {self.time}"