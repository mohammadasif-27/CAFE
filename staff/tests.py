from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from PIL import Image

from accounts.models import Profile
from core.models import ContactMessage
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

    def test_staff_and_owner_home_requests_redirect_to_dashboard(self):
        for user in (self.owner, self.staff):
            with self.subTest(user=user.username):
                self.client.force_login(user)
                response = self.client.get(reverse("home"))
                self.assertRedirects(
                    response,
                    reverse("dashboard"),
                    fetch_redirect_response=False,
                )

        self.client.force_login(self.customer)
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Modern Coffee.")

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
        self.assertEqual(response.context["completed_sales"], Decimal("205.00"))
        self.assertContains(response, reverse("add_food"))
        self.assertContains(response, reverse("edit_food", args=[self.food.pk]))
        self.assertContains(response, "Manage Orders")

    def test_owner_can_see_contact_messages(self):
        ContactMessage.objects.create(
            name="Cafe Visitor",
            email="visitor@example.com",
            phone="9876543210",
            message="Please call me.",
        )
        self.client.force_login(self.owner)

        response = self.client.get(reverse("dashboard"))

        self.assertContains(response, "Contact Messages")
        self.assertContains(response, "Please call me.")

    def test_food_form_rejects_negative_price(self):
        self.client.force_login(self.owner)

        response = self.client.post(reverse("add_food"), {
            "name": "Invalid Food",
            "category": "Coffee",
            "price": "-1.00",
            "available": "on",
        })

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Food.objects.filter(name="Invalid Food").exists())
        self.assertIn("price", response.context["form"].errors)

    def test_owner_can_upload_food_image(self):
        image_buffer = BytesIO()
        Image.new("RGB", (1, 1), color="white").save(image_buffer, format="PNG")
        image = SimpleUploadedFile(
            "latte.png",
            image_buffer.getvalue(),
            content_type="image/png",
        )
        self.client.force_login(self.owner)

        with TemporaryDirectory() as media_root:
            with self.settings(MEDIA_ROOT=media_root):
                response = self.client.post(reverse("add_food"), {
                    "name": "Uploaded Latte",
                    "category": "Coffee",
                    "price": "12.00",
                    "available": "on",
                    "image": image,
                })

                food = Food.objects.get(name="Uploaded Latte")
                self.assertRedirects(response, reverse("add_food"))
                self.assertTrue((Path(media_root) / food.image.name).is_file())

    def test_owner_can_mark_food_unavailable(self):
        self.client.force_login(self.owner)

        response = self.client.post(reverse("edit_food", args=[self.food.pk]), {
            "name": self.food.name,
            "category": self.food.category,
            "price": str(self.food.price),
            "description": self.food.description,
        })

        self.food.refresh_from_db()
        self.assertRedirects(
            response,
            reverse("edit_food", args=[self.food.pk]),
        )
        self.assertFalse(self.food.available)

    def test_owner_can_complete_pending_order(self):
        order = Order.objects.create(
            user=self.customer,
            order_number="CAF-TEST-ORDER",
            customer_name="Cafe Customer",
            phone="1234567890",
            address="1 Main Street",
            city="Sandur",
            pincode="583119",
            subtotal=Decimal("10.00"),
            delivery_fee=Decimal("40.00"),
            total=Decimal("50.00"),
        )
        self.client.force_login(self.owner)

        response = self.client.post(
            reverse("complete_order", args=[order.pk]),
        )

        order.refresh_from_db()
        self.assertRedirects(response, reverse("dashboard"))
        self.assertEqual(order.status, Order.STATUS_COMPLETED)

    def test_completed_sales_add_each_completed_order(self):
        order_data = {
            "user": self.customer,
            "customer_name": "Cafe Customer",
            "phone": "1234567890",
            "address": "1 Main Street",
            "city": "Sandur",
            "pincode": "583119",
            "subtotal": Decimal("100.00"),
            "delivery_fee": Decimal("40.00"),
            "total": Decimal("140.00"),
        }
        first_order = Order.objects.create(
            order_number="CAF-SALES-1",
            status=Order.STATUS_COMPLETED,
            **order_data,
        )
        second_order = Order.objects.create(
            order_number="CAF-SALES-2",
            **order_data,
        )
        yesterday = timezone.now() - timedelta(days=1)
        Order.objects.filter(pk__in=[first_order.pk, second_order.pk]).update(
            created_at=yesterday,
        )
        self.client.force_login(self.owner)

        response = self.client.post(
            reverse("complete_order", args=[second_order.pk]),
        )

        self.assertRedirects(response, reverse("dashboard"))
        dashboard_response = self.client.get(reverse("dashboard"))
        self.assertEqual(
            dashboard_response.context["completed_sales"],
            Decimal("280.00"),
        )

    def test_food_delete_is_post_only(self):
        self.client.force_login(self.owner)

        response = self.client.get(reverse("delete_food", args=[self.food.pk]))

        self.assertEqual(response.status_code, 405)
        self.assertTrue(Food.objects.filter(pk=self.food.pk).exists())

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
        delete_response = self.client.post(
            reverse("delete_food", args=[self.food.pk]),
        )
        order = Order.objects.create(
            user=self.customer,
            order_number="CAF-UNAUTHORIZED",
            customer_name="Cafe Customer",
            phone="1234567890",
            address="1 Main Street",
            city="Sandur",
            pincode="583119",
            subtotal=Decimal("10.00"),
            delivery_fee=Decimal("40.00"),
            total=Decimal("50.00"),
        )
        complete_response = self.client.post(
            reverse("complete_order", args=[order.pk]),
        )

        self.assertEqual(add_response.status_code, 403)
        self.assertEqual(edit_response.status_code, 403)
        self.assertEqual(delete_response.status_code, 403)
        self.assertEqual(complete_response.status_code, 403)
        self.assertFalse(Food.objects.filter(name="Unauthorized Food").exists())
        self.food.refresh_from_db()
        self.assertEqual(self.food.name, "Test Food")

    def test_anonymous_user_is_redirected_to_login(self):
        for url in self.staff_urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 302)
                self.assertIn(reverse("accounts:login"), response["Location"])
