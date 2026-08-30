from django.db import models
from django.contrib.auth.models import User
from menu.models import Food

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField()
    message = models.TextField()

    def __str__(self):
        return self.user.username