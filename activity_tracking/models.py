from django.conf import settings
from django.db import models


class CustomerVisit(models.Model):
    visitor_id = models.UUIDField(db_index=True)
    visit_id = models.UUIDField(unique=True, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='customer_visits',
    )
    started_at = models.DateTimeField(auto_now_add=True)
    last_activity_at = models.DateTimeField()
    last_heartbeat_at = models.DateTimeField(blank=True, null=True)
    ended_at = models.DateTimeField(blank=True, null=True)
    duration_seconds = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['user', 'started_at']),
            models.Index(fields=['visitor_id', 'started_at']),
        ]

    def __str__(self):
        return f'Visit {self.visit_id}'


class CustomerActivity(models.Model):
    LOGIN = 'login'
    PAGE_VIEW = 'page_view'
    FOOD_VIEW = 'food_view'
    SEARCH = 'search'
    CART_ADD = 'cart_add'
    CART_REMOVE = 'cart_remove'
    ORDER_PLACED = 'order_placed'
    CONTACT = 'contact'

    ACTIVITY_TYPES = [
        (LOGIN, 'Login'),
        (PAGE_VIEW, 'Page view'),
        (FOOD_VIEW, 'Food view'),
        (SEARCH, 'Search'),
        (CART_ADD, 'Cart add'),
        (CART_REMOVE, 'Cart remove'),
        (ORDER_PLACED, 'Order placed'),
        (CONTACT, 'Contact'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='customer_activities',
    )
    visit = models.ForeignKey(
        CustomerVisit,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='activities',
    )
    food = models.ForeignKey(
        'menu.Food',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='customer_activities',
    )
    order = models.ForeignKey(
        'orders.Order',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='customer_activities',
    )
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    page = models.CharField(max_length=80, blank=True)
    search_query = models.CharField(max_length=255, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['activity_type', 'timestamp']),
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['food', 'timestamp']),
        ]

    def __str__(self):
        return f'{self.get_activity_type_display()} at {self.timestamp}'
