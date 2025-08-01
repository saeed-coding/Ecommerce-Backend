from django.contrib.auth.models import AbstractUser
import secrets
from django.conf import settings
from django.db import models
from django.utils import timezone


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, unique=True)
    whatsapp = models.CharField(max_length=20, blank=True)
    is_admin = models.BooleanField(default=False)


class UserToken(models.Model):
    key = models.CharField(max_length=40, unique=True, db_index=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='auth_tokens', on_delete=models.CASCADE)
    name = models.CharField(max_length=120, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    last_used = models.DateTimeField(null=True, blank=True)

    ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = secrets.token_hex(20)
        return super().save(*args, **kwargs)