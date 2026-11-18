from django.utils.timezone import now

from .models import CustomerActivity
from .services import get_visit


PAGE_NAMES = {
    'home': 'Home / Menu',
    'accounts:login': 'Login',
    'accounts:register': 'Register',
    'accounts:profile': 'Profile',
    'accounts:edit_profile': 'Profile',
    'orders:cart': 'Cart',
    'orders:checkout': 'Checkout',
    'orders:my_orders': 'Orders',
    'orders:order_success': 'Orders',
    'menu:food_detail': 'Food Details',
}


class ActivityTrackingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if (
            request.method != 'GET'
            or response.status_code != 200
            or not response.get('Content-Type', '').startswith('text/html')
        ):
            return response

        match = getattr(request, 'resolver_match', None)
        page = PAGE_NAMES.get(match.view_name if match else None)
        if page is None:
            return response

        visit = get_visit(request, at=now())
        if visit is None:
            return response

        food = None
        if match.view_name == 'menu:food_detail':
            from menu.models import Food

            food_id = match.kwargs.get('food_id')
            food = Food.objects.filter(pk=food_id).first()

        visit.last_activity_at = now()
        visit.ended_at = None
        visit.save(update_fields=['last_activity_at', 'ended_at'])
        CustomerActivity.objects.create(
            user=visit.user,
            visit=visit,
            food=food,
            activity_type=CustomerActivity.PAGE_VIEW,
            page=page,
        )
        return response
