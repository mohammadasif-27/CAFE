from django.db import models


class Food(models.Model):
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=60)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    available = models.BooleanField(default=True)
    image = models.CharField(
        max_length=255,
        blank=True,
        help_text="Relative static image path, for example 'images/cappuccino.svg'."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def subtotal(self):
        return self.price
