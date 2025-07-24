from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, unique=True)
    whatsapp = models.CharField(max_length=20, blank=True)
    is_admin = models.BooleanField(default=False)
