from django.test import TestCase
from django.contrib.auth.models import User
from django.test import override_settings

from accounts.models import Profile


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
    def test_configured_owner_code_preserves_owner_registration(self):
        response = self.client.post(
            "/accounts/register/",
            self.registration_data("test-owner-code"),
        )

        self.assertRedirects(response, "/accounts/login/")
        user = User.objects.get(username="new-owner")
        self.assertEqual(user.profile.account_type, "owner")
