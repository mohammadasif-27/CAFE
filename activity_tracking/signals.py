from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver

from .models import CustomerActivity
from .services import record_activity


@receiver(user_logged_in)
def track_customer_login(sender, request, user, **kwargs):
    if request is not None:
        if not hasattr(request, 'user'):
            request.user = user
        record_activity(
            request,
            CustomerActivity.LOGIN,
            page='Login',
        )
