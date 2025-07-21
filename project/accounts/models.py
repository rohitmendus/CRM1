from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('manager', 'Manager'),
        ('engineer', 'Site Engineer'),
        ('assistant', 'Office Assistant'),
    ]

    role = models.CharField(choices=ROLE_CHOICES, max_length=100)
    email = models.EmailField(unique=True, blank=False)

    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"