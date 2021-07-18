from django.core.validators import EmailValidator
from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    username = models.CharField(max_length=126, unique=True)
    first_name = models.CharField(max_length=126)
    last_name = models.CharField(max_length=126, null=True, blank=True)
    email = models.EmailField(unique=True, validators=[EmailValidator])

    def __str__(self):
        return self.username

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
