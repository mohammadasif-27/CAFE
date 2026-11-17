from django.db import models
from django.contrib.auth.models import User
from menu.models import Food

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    food = models.ForeignKey(
        Food,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    rating = models.IntegerField(choices=[(value, value) for value in range(1, 6)])
    message = models.TextField()

    def __str__(self):
        return self.user.username


class ContactMessage(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField(max_length=254)
    phone = models.CharField(max_length=20)
    message = models.TextField(max_length=2000)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Contact message from {self.name}"