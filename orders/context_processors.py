from django.db.models import Sum


def cart_quantity(request):
    if request.user.is_authenticated:
        total = request.user.cart_items.aggregate(quantity=Sum('quantity'))['quantity']
        return {'cart_quantity': total or 0}
    return {'cart_quantity': 0}
