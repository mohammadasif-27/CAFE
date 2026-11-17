from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.models import Profile
from menu.models import Food
from orders.models import Order

# Create your tests here.


class StaffAccessTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.owner = user_model.objects.create_user(
            username="owner",
            password="test-password",
        )
        Profile.objects.create(user=self.owner, account_type="owner")

        self.staff = user_model.objects.create_user(
            username="staff",
            password="test-password",
            is_staff=True,
        )

        self.customer = user_model.objects.create_user(
            username="customer",
            password="test-password",
        )
        Profile.objects.create(user=self.customer, account_type="customer")

        self.food = Food.objects.create(
            name="Test Food",
            category="Coffee",
            price="10.00",
        )
        self.staff_urls = [
            reverse("dashboard"),
            reverse("add_food"),
            reverse("edit_food", args=[self.food.pk]),
        ]

    def test_owner_can_access_all_staff_pages(self):
        self.client.force_login(self.owner)
        for url in self.staff_urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, "CafeHub")
                self.assertContains(response, "Owner / Staff")
                self.assertContains(response, "Manage Foods")
                self.assertContains(response, "Orders")
                self.assertContains(response, "Logout")

    def test_customer_pages_keep_customer_navbar(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Login")
        self.assertNotContains(response, "Owner / Staff")

    def test_dashboard_shows_requested_database_totals(self):
        Order.objects.create(
            user=self.customer,
            order_number="CAF-TEST-1",
            customer_name="Cafe Customer",
            phone="1234567890",
            address="1 Main Street",
            city="Sandur",
            pincode="583119",
            subtotal=Decimal("100.00"),
            delivery_fee=Decimal("40.00"),
            total=Decimal("140.00"),
            status=Order.STATUS_COMPLETED,
        )
        old_order = Order.objects.create(
            user=self.customer,
            order_number="CAF-TEST-3",
            customer_name="Cafe Customer",
            phone="1234567890",
            address="1 Main Street",
            city="Sandur",
            pincode="583119",
            subtotal=Decimal("25.00"),
            delivery_fee=Decimal("40.00"),
            total=Decimal("65.00"),
            status=Order.STATUS_COMPLETED,
        )
        Order.objects.filter(pk=old_order.pk).update(
            created_at=timezone.now() - timedelta(days=1),
        )
        Order.objects.create(
            user=self.customer,
            order_number="CAF-TEST-2",
            customer_name="Cafe Customer",
            phone="1234567890",
            address="1 Main Street",
            city="Sandur",
            pincode="583119",
            subtotal=Decimal("50.00"),
            delivery_fee=Decimal("40.00"),
            total=Decimal("90.00"),
            status=Order.STATUS_PENDING,
        )

        self.client.force_login(self.owner)
        response = self.client.get(reverse("dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["total_foods"], Food.objects.count())
        self.assertEqual(
            response.context["available_foods"],
            Food.objects.filter(available=True).count(),
        )
        self.assertEqual(response.context["total_orders"], 3)
        self.assertEqual(response.context["pending_orders"], 1)
        self.assertEqual(response.context["total_customers"], 1)
        self.assertEqual(response.context["today_sales"], Decimal("140.00"))
        self.assertContains(response, reverse("add_food"))
        self.assertContains(response, reverse("edit_food", args=[self.food.pk]))
        self.assertContains(response, "Manage Orders")

    def test_django_staff_user_can_access_all_staff_pages(self):
        self.client.force_login(self.staff)
        for url in self.staff_urls:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)

    def test_customer_is_forbidden_from_all_staff_pages_and_actions(self):
        self.client.force_login(self.customer)
        for url in self.staff_urls:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 403)

        add_response = self.client.post(reverse("add_food"), {
            "name": "Unauthorized Food",
            "category": "Coffee",
            "price": "12.00",
        })
        edit_response = self.client.post(
            reverse("edit_food", args=[self.food.pk]),
            {"name": "Changed Food", "category": "Coffee", "price": "12.00"},
        )

        self.assertEqual(add_response.status_code, 403)
        self.assertEqual(edit_response.status_code, 403)
        self.assertFalse(Food.objects.filter(name="Unauthorized Food").exists())
        self.food.refresh_from_db()
        self.assertEqual(self.food.name, "Test Food")

    def test_anonymous_user_is_redirected_to_login(self):
        for url in self.staff_urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 302)
                self.assertIn(reverse("accounts:login"), response["Location"])
