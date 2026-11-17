from django.test import TestCase
from django.contrib.auth.models import User

from core.models import ContactMessage, Review


class ContactWorkflowTests(TestCase):
    def test_contact_submission_is_saved(self):
        response = self.client.post("/", {
            "name": "Cafe Customer",
            "email": "customer@example.com",
            "phone": "+91 98765 43210",
            "message": "Please share your opening hours.",
        })

        self.assertRedirects(response, "/#contact", fetch_redirect_response=False)
        self.assertEqual(ContactMessage.objects.count(), 1)

    def test_invalid_contact_submission_is_not_saved(self):
        response = self.client.post("/", {
            "name": "Cafe Customer",
            "email": "customer@example.com",
            "phone": "not a phone",
            "message": "Please share your opening hours.",
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(ContactMessage.objects.count(), 0)
        self.assertContains(response, "Enter a valid value.")


class ReviewWorkflowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="reviewer",
            password="test-password",
        )
        self.client.force_login(self.user)

    def test_valid_review_is_saved(self):
        response = self.client.post("/add-review/", {
            "rating": "5",
            "message": "Great coffee.",
        })

        self.assertRedirects(response, "/")
        self.assertEqual(Review.objects.get().rating, 5)

    def test_out_of_range_review_is_rejected(self):
        response = self.client.post("/add-review/", {
            "rating": "9",
            "message": "Great coffee.",
        })

        self.assertRedirects(response, "/")
        self.assertFalse(Review.objects.exists())
