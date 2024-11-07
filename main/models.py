from django.db import models # type: ignore
from django.contrib.auth import get_user_model # type: ignore
import uuid
from datetime import datetime
from django.utils import timezone # type: ignore

User = get_user_model()

# Create your models here.
class Profile(models.Model):
    id_user = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profileimg = models.ImageField(upload_to='profile_images', default='blank-profile-picture.png')
    firstname = models.CharField(max_length=50, blank=True, null=True)
    lastname = models.CharField(max_length=50, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    gender = models.CharField(max_length=10, blank=True, null=True)
    department = models.CharField(max_length=50, blank=True, null=True)
    country = models.CharField(max_length=50, blank=True, null=True)
    province = models.CharField(max_length=50, blank=True, null=True)
    city = models.CharField(max_length=50, blank=True, null=True)
    mobile_no = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.user.username

    @property
    def email(self):
        return self.user.email
    


class ChurnPrediction(models.Model):
    
    customer_id = models.CharField(max_length=50, null=True, blank=True)
    age = models.IntegerField(default=0)
    senior_citizen = models.CharField(max_length=5, null=True, blank=True)
    gender = models.CharField(max_length=10, null=True, blank=True)
    location = models.CharField(max_length=100, null=True, blank=True)
    tenure = models.IntegerField(default=0)
    total_day_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_night_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_eve_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_intl_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    prediction_output = models.TextField(null=True, blank=True)
    prediction_details = models.TextField(null=True, blank=True)
    recommendations = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def total_charges(self):
        return (
            self.total_day_charge +
            self.total_night_charge +
            self.total_eve_charge +
            self.total_intl_charge
        )

    def __str__(self):
        return f"Customer {self.customer_id} - Churn Probability: {self.churn_rate}%"
       