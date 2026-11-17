from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse

from menu.models import Food
from orders.models import CartItem, Order


class CheckoutWorkflowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="checkout-customer",
            password="test-password",
        )
        self.food = Food.objects.create(
            name="Latte",
            category="Coffee",
            price="120.00",
        )
        CartItem.objects.create(user=self.user, food=self.food, quantity=2)
        self.client.force_login(self.user)

    def test_invalid_delivery_data_does_not_create_order(self):
        response = self.client.post(reverse("orders:place_order"), {
            "name": "Customer",
            "phone": "invalid",
            "address": "1 Main Street",
            "city": "Sandur",
            "pincode": "123",
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["form"].errors.keys(), {"phone", "pincode"})
        self.assertFalse(Order.objects.exists())
        self.assertTrue(CartItem.objects.filter(user=self.user).exists())

    def test_valid_delivery_data_creates_order_and_clears_cart(self):
        response = self.client.post(reverse("orders:place_order"), {
            "name": "Customer",
            "phone": "+91 98765 43210",
            "address": "1 Main Street",
            "city": "Sandur",
            "pincode": "583119",
        })

        order = Order.objects.get(user=self.user)
        self.assertRedirects(
            response,
            reverse("orders:order_success", args=[order.order_number]),
            fetch_redirect_response=False,
        )
        self.assertEqual(order.total, order.subtotal + order.delivery_fee)
        self.assertFalse(CartItem.objects.filter(user=self.user).exists())

    def test_cart_image_uses_media_url(self):
        self.food.image = "foods/latte.jpg"
        self.food.save(update_fields=["image"])

        response = self.client.get(reverse("orders:cart"))

        self.assertContains(response, "/media/foods/latte.jpg")

    def test_external_referer_is_not_used_for_redirect(self):
        response = self.client.get(
            reverse("orders:add_to_cart", args=[self.food.pk]),
            HTTP_REFERER="https://example.invalid/",
        )

        self.assertRedirects(response, "/", fetch_redirect_response=False)
