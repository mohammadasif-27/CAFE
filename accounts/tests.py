from decimal import Decimal

from django.test import TestCase
from django.contrib.auth.models import User
from django.test import override_settings
from django.urls import reverse

from accounts.models import Profile
from menu.models import Food
from orders.models import CartItem, Order


class OwnerRegistrationTests(TestCase):
    def registration_data(self, owner_code):
        return {
            "first_name": "Cafe",
            "last_name": "Owner",
            "username": "new-owner",
            "email": "owner@example.com",
            "password1": "StrongPassword!837",
            "password2": "StrongPassword!837",
            "account_type": "owner",
            "owner_code": owner_code,
        }

    @override_settings(OWNER_ACCESS_CODE=None)
    def test_hard_coded_code_does_not_grant_owner_access(self):
        response = self.client.post(
            "/accounts/register/",
            self.registration_data("1234"),
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="new-owner").exists())

    @override_settings(OWNER_ACCESS_CODE="test-owner-code")
    def test_invalid_account_type_is_rejected(self):
        data = self.registration_data("test-owner-code")
        data["account_type"] = "administrator"

        response = self.client.post("/accounts/register/", data)

        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="new-owner").exists())

    @override_settings(OWNER_ACCESS_CODE="test-owner-code")
    def test_configured_owner_code_preserves_owner_registration(self):
        response = self.client.post(
            "/accounts/register/",
            self.registration_data("test-owner-code"),
        )

        self.assertRedirects(response, "/accounts/login/")
        user = User.objects.get(username="new-owner")
        self.assertEqual(user.profile.account_type, "owner")


class AccountLoginTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="cafe-customer",
            email="customer@example.com",
            password="StrongPassword!837",
        )
        Profile.objects.create(user=self.user, account_type="customer")

    def test_login_accepts_email_address(self):
        response = self.client.post("/accounts/login/", {
            "login": "CUSTOMER@example.com",
            "password": "StrongPassword!837",
        })

        self.assertRedirects(response, "/")

    def test_login_honors_only_safe_next_url(self):
        response = self.client.post("/accounts/login/", {
            "login": self.user.username,
            "password": "StrongPassword!837",
            "next": "/orders/cart/",
        })
        self.assertRedirects(response, "/orders/cart/", fetch_redirect_response=False)

        self.client.logout()
        response = self.client.post("/accounts/login/", {
            "login": self.user.username,
            "password": "StrongPassword!837",
            "next": "https://example.invalid/",
        })
        self.assertRedirects(response, "/", fetch_redirect_response=False)

    def test_staff_without_profile_can_sign_in(self):
        staff_user = User.objects.create_user(
            username="profileless-staff",
            password="StrongPassword!837",
            is_staff=True,
        )

        response = self.client.post("/accounts/login/", {
            "login": staff_user.username,
            "password": "StrongPassword!837",
        })

        self.assertRedirects(
            response,
            "/staff/",
            fetch_redirect_response=False,
        )
        self.assertEqual(self.client.get(reverse("home")).status_code, 200)

    def test_pending_cart_add_is_completed_after_login(self):
        food = Food.objects.create(name="Latte", category="Coffee", price="5.00")
        session = self.client.session
        session["pending_cart_action"] = {
            "food_id": food.pk,
            "action": "add",
        }
        session.save()

        response = self.client.post("/accounts/login/", {
            "login": self.user.username,
            "password": "StrongPassword!837",
        })

        self.assertRedirects(response, "/orders/cart/", fetch_redirect_response=False)
        self.assertEqual(
            CartItem.objects.get(user=self.user, food=food).quantity,
            1,
        )

    def test_profile_displays_order_statistics(self):
        order_data = {
            "user": self.user,
            "customer_name": "Cafe Customer",
            "phone": "9876543210",
            "address": "1 Main Street",
            "city": "Sandur",
            "pincode": "583119",
            "subtotal": Decimal("100.00"),
            "delivery_fee": Decimal("40.00"),
            "total": Decimal("140.00"),
        }
        Order.objects.create(
            order_number="CAF-PROFILE-1",
            status=Order.STATUS_COMPLETED,
            **order_data,
        )
        Order.objects.create(
            order_number="CAF-PROFILE-2",
            status=Order.STATUS_PENDING,
            **order_data,
        )
        self.client.force_login(self.user)

        response = self.client.get(reverse("accounts:profile"))

        self.assertEqual(response.context["orders_count"], 2)
        self.assertEqual(response.context["completed_orders"], 1)
        self.assertEqual(response.context["pending_orders"], 1)
        self.assertEqual(len(response.context["recent_orders"]), 2)

    def test_logout_requires_post(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("accounts:logout"))

        self.assertEqual(response.status_code, 405)
        self.assertTrue(response.wsgi_request.user.is_authenticated)

        response = self.client.post(reverse("accounts:logout"))

        self.assertRedirects(response, "/")
