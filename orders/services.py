from .models import CartItem


def add_food_to_cart(user, food):
    cart_item, created = CartItem.objects.get_or_create(user=user, food=food)
    if not created:
        cart_item.quantity += 1
        cart_item.save(update_fields=['quantity', 'updated_at'])
    return cart_item
