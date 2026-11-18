from datetime import timedelta
from uuid import UUID, uuid4

from django.contrib.auth.models import AnonymousUser
from django.utils import timezone

from accounts.models import Profile

from .models import CustomerActivity, CustomerVisit


INACTIVITY_TIMEOUT = timedelta(minutes=30)
MAX_HEARTBEAT_SECONDS = 90


def _tracked_user(user):
    if not getattr(user, 'is_authenticated', False) or user.is_staff:
        return None

    account_type = Profile.objects.filter(user_id=user.pk).values_list(
        'account_type',
        flat=True,
    ).first()
    if account_type == 'owner':
        return None
    return user


def get_visit(request, at=None):
    at = at or timezone.now()
    request_user = getattr(request, 'user', AnonymousUser())
    user = _tracked_user(request_user)
    if getattr(request_user, 'is_authenticated', False) and user is None:
        return None

    visitor_id_value = request.session.get('activity_visitor_id')
    try:
        visitor_id = UUID(visitor_id_value)
    except (TypeError, ValueError, AttributeError):
        visitor_id = uuid4()
        request.session['activity_visitor_id'] = str(visitor_id)

    visit_id_value = request.session.get('activity_visit_id')
    try:
        visit_id = UUID(visit_id_value)
    except (TypeError, ValueError, AttributeError):
        visit_id = None

    visit = CustomerVisit.objects.filter(visit_id=visit_id).first() if visit_id else None
    if visit and (
        at - visit.last_activity_at >= INACTIVITY_TIMEOUT
        or (visit.user_id and user and visit.user_id != user.pk)
    ):
        if visit.ended_at is None:
            visit.ended_at = visit.last_activity_at
            visit.save(update_fields=['ended_at'])
        visit = None

    if visit is None:
        visit_id = uuid4()
        visit = CustomerVisit.objects.create(
            visitor_id=visitor_id,
            visit_id=visit_id,
            user=user,
            last_activity_at=at,
            last_heartbeat_at=at,
        )
        request.session['activity_visit_id'] = str(visit_id)

    if user and visit.user_id is None:
        visit.user = user
        visit.save(update_fields=['user'])
        CustomerActivity.objects.filter(
            visit=visit,
            user__isnull=True,
        ).update(user=user)

    return visit


def record_activity(
    request,
    activity_type,
    *,
    page='',
    food=None,
    order=None,
    search_query='',
    at=None,
):
    at = at or timezone.now()
    visit = get_visit(request, at=at)
    if visit is None:
        return None

    visit.last_activity_at = at
    visit.ended_at = None
    visit.save(update_fields=['last_activity_at', 'ended_at'])
    return CustomerActivity.objects.create(
        user=visit.user,
        visit=visit,
        activity_type=activity_type,
        page=page,
        food=food,
        order=order,
        search_query=search_query[:255],
        timestamp=at,
    )


def record_heartbeat(request, at=None):
    at = at or timezone.now()
    visit = get_visit(request, at=at)
    if visit is None:
        return None

    elapsed = 0
    if visit.last_heartbeat_at:
        elapsed = max(
            0,
            min(
                round((at - visit.last_heartbeat_at).total_seconds()),
                MAX_HEARTBEAT_SECONDS,
            ),
        )

    visit.duration_seconds += elapsed
    visit.last_heartbeat_at = at
    visit.last_activity_at = at
    visit.ended_at = None
    visit.save(update_fields=[
        'duration_seconds',
        'last_heartbeat_at',
        'last_activity_at',
        'ended_at',
    ])
    return visit
