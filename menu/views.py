from django.shortcuts import get_object_or_404, render

from activity_tracking.models import CustomerActivity
from activity_tracking.services import record_activity
from .models import Food


def food_detail(request, food_id):
    food = get_object_or_404(Food, pk=food_id, available=True)
    response = render(request, 'menu/food_detail.html', {'food': food})
    record_activity(
        request,
        CustomerActivity.FOOD_VIEW,
        page='Food Details',
        food=food,
    )
    return response
