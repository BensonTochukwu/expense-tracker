from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    # Additional fields
    profile_pic = models.ImageField(upload_to='profile_pic/', null=True, blank=True)

    def __str__(self):
        return self.username

class Regusers(models.Model):
    admin = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    mobilenumber = models.CharField(max_length=15)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.admin.first_name + self.admin.last_name


class Expenses(models.Model):
    deuser_id = models.ForeignKey(Regusers, on_delete=models.CASCADE)
    dateofexpenses = models.DateField()
    item = models.CharField(max_length=250)
    cost = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.item


