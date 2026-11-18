from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .models import CustomerActivity
from .services import record_activity, record_heartbeat


@require_POST
def heartbeat(request):
    record_heartbeat(request)
    return JsonResponse({'ok': True})


@require_POST
def client_event(request):
    event_type = request.POST.get('type')
    page = request.POST.get('page')
    if event_type != CustomerActivity.PAGE_VIEW or page not in {'Menu', 'Contact'}:
        return JsonResponse({'error': 'Unsupported activity.'}, status=400)

    record_activity(request, event_type, page=page)
    return JsonResponse({'ok': True})
