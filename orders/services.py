from django.db import transaction

from activity_tracking.models import CustomerActivity
from activity_tracking.services import record_activity

from .models import CartItem


@transaction.atomic
def add_food_to_cart(user, food, request=None):
    cart_item, created = CartItem.objects.get_or_create(user=user, food=food)
    if not created:
        cart_item.quantity += 1
        cart_item.save(update_fields=['quantity', 'updated_at'])
    if request is not None:
        record_activity(
            request,
            CustomerActivity.CART_ADD,
            page='Cart',
            food=food,
        )
    return cart_item
