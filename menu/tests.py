from pathlib import Path

from django.conf import settings
from django.test import TestCase
from django.urls import reverse

from .models import Food


class FoodImageTests(TestCase):
    def test_seeded_menu_photos_exist_and_render(self):
        foods = list(Food.objects.all())
        self.assertTrue(foods)

        page = self.client.get(reverse('home'))
        self.assertEqual(page.status_code, 200)

        for food in foods:
            with self.subTest(food=food.name):
                self.assertTrue(food.image)
                self.assertTrue(Path(settings.MEDIA_ROOT, food.image.name).is_file())
                self.assertContains(page, food.image.url)

    def test_menu_without_an_image_uses_the_photo_fallback(self):
        Food.objects.create(
            name='Image-less test item',
            category='Test',
            price='1.00',
            available=True,
        )

        page = self.client.get(reverse('home'))
        self.assertContains(page, '/static/images/default-food.jpg')
        self.assertTrue(
            Path(settings.BASE_DIR, 'static', 'images', 'default-food.jpg').is_file()
        )
