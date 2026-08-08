from django.conf import settings
from django.db import models


class CartItem(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cart_items'
    )
    food = models.ForeignKey(
        'menu.Food',
        on_delete=models.CASCADE,
        related_name='cart_items'
    )
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'food')
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.food.name} x {self.quantity} ({self.user.username})"

    @property
    def subtotal(self):
        return self.food.price * self.quantity
