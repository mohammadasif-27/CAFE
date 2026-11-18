from datetime import timedelta
from decimal import Decimal

from django.db.models import Avg, Count, F, Max, Min, Sum
from django.utils import timezone

from accounts.models import Profile
from orders.models import Order, OrderItem

from .models import CustomerActivity, CustomerVisit


def get_analytics_summary():
    close_inactive_visits()
    total_spent = Order.objects.aggregate(total=Sum('total'))['total'] or Decimal('0.00')
    average_order_value = Order.objects.aggregate(average=Avg('total'))['average']

    return {
        'total_customers': Profile.objects.filter(account_type='customer').count(),
        'total_visits': CustomerVisit.objects.count(),
        'total_visitors': CustomerVisit.objects.values('visitor_id').distinct().count(),
        'returning_visitors': CustomerVisit.objects.values('visitor_id')
        .annotate(visit_count=Count('id'))
        .filter(visit_count__gt=1)
        .count(),
        'total_orders': Order.objects.count(),
        'repeat_customers': Order.objects.values('user_id')
        .annotate(order_count=Count('id'))
        .filter(order_count__gt=1)
        .count(),
        'total_spent': total_spent,
        'average_order_value': average_order_value or Decimal('0.00'),
        'total_session_seconds': CustomerVisit.objects.aggregate(
            total=Sum('duration_seconds'),
        )['total'] or 0,
        'most_viewed_foods': CustomerActivity.objects.filter(
            activity_type=CustomerActivity.FOOD_VIEW,
            food__isnull=False,
        ).values(
            'food__name',
        ).annotate(
            views=Count('id'),
        ).order_by(
            '-views',
            'food__name',
        )[:5],
        'most_viewed_categories': CustomerActivity.objects.filter(
            activity_type=CustomerActivity.FOOD_VIEW,
            food__isnull=False,
        ).values(
            'food__category',
        ).annotate(
            views=Count('id'),
        ).order_by(
            '-views',
            'food__category',
        )[:5],
        'most_searched_foods': CustomerActivity.objects.filter(
            activity_type=CustomerActivity.SEARCH,
        ).values(
            'search_query',
        ).annotate(
            searches=Count('id'),
        ).order_by(
            '-searches',
            'search_query',
        )[:5],
        'most_ordered_foods': OrderItem.objects.values(
            'food__name',
        ).annotate(
            quantity=Sum('quantity'),
        ).order_by(
            '-quantity',
            'food__name',
        )[:5],
        'most_active_customers': CustomerActivity.objects.filter(
            user__isnull=False,
        ).values(
            'user__username',
        ).annotate(
            activity_count=Count('id'),
        ).order_by(
            '-activity_count',
            'user__username',
        )[:5],
        'customer_visit_stats': get_customer_visit_stats(),
        'customer_order_stats': get_customer_order_stats(),
        'customers_without_recent_orders': customers_without_recent_orders(),
    }


def get_customer_visit_stats():
    return CustomerVisit.objects.filter(
        user__isnull=False,
    ).values(
        'user_id',
        'user__username',
    ).annotate(
        visit_count=Count('id'),
        first_visit=Min('started_at'),
        last_visit=Max('last_activity_at'),
        total_session_seconds=Sum('duration_seconds'),
    ).order_by(
        '-visit_count',
        'user__username',
    )


def get_customer_order_stats():
    return Order.objects.values(
        'user_id',
        'user__username',
    ).annotate(
        order_count=Count('id'),
        total_spent=Sum('total'),
        average_order_value=Avg('total'),
        last_order=Max('created_at'),
    ).order_by(
        '-order_count',
        'user__username',
    )


def close_inactive_visits(at=None):
    at = at or timezone.now()
    cutoff = at - timedelta(minutes=30)
    CustomerVisit.objects.filter(
        ended_at__isnull=True,
        last_activity_at__lte=cutoff,
    ).update(ended_at=F('last_activity_at'))


def customers_without_recent_orders(days=30):
    cutoff = timezone.now() - timedelta(days=days)
    recent_customer_ids = Order.objects.filter(
        created_at__gte=cutoff,
    ).values('user_id')
    return Profile.objects.filter(
        account_type='customer',
    ).exclude(
        user_id__in=recent_customer_ids,
    ).select_related(
        'user',
    ).order_by(
        'user__username',
    )
