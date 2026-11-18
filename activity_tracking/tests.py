from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.models import Profile
from menu.models import Food
from orders.models import CartItem, Order

from .models import CustomerActivity, CustomerVisit


class CustomerActivityTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='activity-customer',
            email='activity@example.test',
            password='test-password',
        )
        Profile.objects.create(user=self.user, account_type='customer')
        self.food = Food.objects.create(
            name='Activity Latte',
            category='Coffee',
            price=Decimal('5.00'),
        )

    def test_anonymous_page_view_uses_anonymous_safe_visit_id(self):
        response = self.client.get(reverse('home'))

        self.assertEqual(response.status_code, 200)
        activity = CustomerActivity.objects.get(
            activity_type=CustomerActivity.PAGE_VIEW,
            page='Home / Menu',
        )
        self.assertIsNone(activity.user)
        self.assertIsNotNone(activity.visit)
        self.assertIsNotNone(self.client.session.get('activity_visitor_id'))

    def test_successful_login_is_tracked_and_associates_the_current_visit(self):
        self.client.get(reverse('home'))
        response = self.client.post(reverse('accounts:login'), {
            'login': self.user.username,
            'password': 'test-password',
        })

        self.assertEqual(response.status_code, 302)
        login_event = CustomerActivity.objects.get(
            activity_type=CustomerActivity.LOGIN,
        )
        self.assertEqual(login_event.user, self.user)
        self.assertEqual(login_event.visit.user, self.user)
        self.assertTrue(
            CustomerActivity.objects.filter(
                page='Home / Menu',
                user=self.user,
            ).exists()
        )

    def test_food_detail_records_page_and_food_view(self):
        response = self.client.get(
            reverse('menu:food_detail', args=[self.food.pk]),
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(CustomerActivity.objects.filter(
            activity_type=CustomerActivity.FOOD_VIEW,
            food=self.food,
        ).exists())
        self.assertTrue(CustomerActivity.objects.filter(
            activity_type=CustomerActivity.PAGE_VIEW,
            page='Food Details',
            food=self.food,
        ).exists())

    def test_cart_add_and_remove_are_recorded(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse('orders:add_to_cart', args=[self.food.pk]),
        )
        cart_item = CartItem.objects.get(user=self.user, food=self.food)

        self.assertEqual(response.status_code, 302)
        self.assertTrue(CustomerActivity.objects.filter(
            activity_type=CustomerActivity.CART_ADD,
            food=self.food,
            user=self.user,
        ).exists())

        self.client.post(
            reverse('orders:update_cart_item', args=[cart_item.pk]),
            {'action': 'remove'},
        )
        self.assertTrue(CustomerActivity.objects.filter(
            activity_type=CustomerActivity.CART_REMOVE,
            food=self.food,
            user=self.user,
        ).exists())
        self.assertFalse(CartItem.objects.filter(pk=cart_item.pk).exists())

    def test_order_placement_is_tracked_using_existing_order(self):
        self.client.force_login(self.user)
        CartItem.objects.create(user=self.user, food=self.food, quantity=2)
        response = self.client.post(reverse('orders:place_order'), {
            'name': 'Cafe Customer',
            'phone': '+91 98765 43210',
            'address': '1 Main Street',
            'city': 'Sandur',
            'pincode': '583119',
        })

        order = Order.objects.get(user=self.user)
        event = CustomerActivity.objects.get(
            activity_type=CustomerActivity.ORDER_PLACED,
            order=order,
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(event.user, self.user)
        self.assertEqual(order.items.count(), 1)

    def test_heartbeat_accumulates_capped_session_duration(self):
        self.client.get(reverse('home'))
        visit = CustomerVisit.objects.get()
        previous_heartbeat = timezone.now() - timedelta(seconds=75)
        CustomerVisit.objects.filter(pk=visit.pk).update(
            last_heartbeat_at=previous_heartbeat,
        )

        response = self.client.post(reverse('activity_tracking:heartbeat'))

        visit.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(visit.duration_seconds, 75)
        self.assertIsNone(visit.ended_at)

    def test_inactivity_starts_a_new_visit_and_closes_the_previous_one(self):
        self.client.get(reverse('home'))
        previous_visit = CustomerVisit.objects.get()
        last_activity = timezone.now() - timedelta(minutes=31)
        CustomerVisit.objects.filter(pk=previous_visit.pk).update(
            last_activity_at=last_activity,
        )

        self.client.get(reverse('home'))

        previous_visit.refresh_from_db()
        visits = CustomerVisit.objects.order_by('started_at')
        self.assertEqual(visits.count(), 2)
        self.assertEqual(previous_visit.ended_at, last_activity)
        self.assertEqual(
            visits.first().visitor_id,
            visits.last().visitor_id,
        )

    def test_activity_endpoint_rejects_non_post_and_unknown_data(self):
        self.assertEqual(
            self.client.get(reverse('activity_tracking:heartbeat')).status_code,
            405,
        )
        response = self.client.post(reverse('activity_tracking:event'), {
            'type': 'page_view',
            'page': 'Private Profile',
        })
        self.assertEqual(response.status_code, 400)

    def test_activity_endpoint_requires_csrf_protection(self):
        client = Client(enforce_csrf_checks=True)
        client.get(reverse('home'))
        token = client.cookies['csrftoken'].value

        response = client.post(
            reverse('activity_tracking:heartbeat'),
            HTTP_X_CSRFTOKEN=token,
        )

        self.assertEqual(response.status_code, 200)

    def test_contact_submission_is_recorded_without_customer_personal_details(self):
        response = self.client.post(reverse('home'), {
            'name': 'Cafe Visitor',
            'email': 'visitor@example.test',
            'phone': '9876543210',
            'message': 'Please share your opening hours.',
        })

        self.assertEqual(response.status_code, 302)
        event = CustomerActivity.objects.get(
            activity_type=CustomerActivity.CONTACT,
        )
        self.assertEqual(event.page, 'Contact')
        self.assertIsNone(event.user)
        self.assertFalse(hasattr(event, 'phone'))

    def test_customer_cannot_access_owner_analytics(self):
        self.client.force_login(self.user)

        self.assertEqual(
            self.client.get(reverse('analytics')).status_code,
            403,
        )

    def test_owner_analytics_shows_activity_and_order_summaries(self):
        owner = get_user_model().objects.create_user(
            username='analytics-owner',
            password='test-password',
        )
        Profile.objects.create(user=owner, account_type='owner')
        self.client.force_login(self.user)
        self.client.get(reverse('menu:food_detail', args=[self.food.pk]))
        self.client.post(reverse('orders:add_to_cart', args=[self.food.pk]))
        cart_item = CartItem.objects.get(user=self.user, food=self.food)
        self.client.post(
            reverse('orders:update_cart_item', args=[cart_item.pk]),
            {'action': 'remove'},
        )
        order = Order.objects.create(
            user=self.user,
            order_number='CAF-ANALYTICS',
            customer_name='Cafe Customer',
            phone='1234567890',
            address='1 Main Street',
            city='Sandur',
            pincode='583119',
            subtotal=Decimal('10.00'),
            delivery_fee=Decimal('40.00'),
            total=Decimal('50.00'),
        )
        self.client.force_login(owner)

        response = self.client.get(reverse('analytics'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['total_customers'], 1)
        self.assertEqual(response.context['most_viewed_foods'][0]['food__name'], self.food.name)
        self.assertEqual(response.context['customer_visit_stats'][0]['visit_count'], 1)
        self.assertEqual(response.context['customer_order_stats'][0]['order_count'], 1)
        self.assertEqual(response.context['customer_order_stats'][0]['total_spent'], order.total)
        self.assertContains(response, 'Customer Analytics')
        self.assertContains(response, 'Activity Latte')
