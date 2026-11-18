from django.db import migrations
from django.db.models import Q


FOOD_IMAGES = {
    'Almond Croissant': 'foods/Almond_Croissant.jpg',
    'Cappuccino': 'foods/Cappuccino.jpg',
    'Cheese Pizza': 'foods/pepperoni_cheese_pizza.jpg',
    'Chocolate Cake': 'foods/Chocolate_Cake.jpg',
    'Classic Burger': 'foods/Classic_Burger.jpg',
    'Espresso Shot': 'foods/Espresso_Shot_rmDIWoZ.jpg',
    'Ginger Tea': 'foods/ginger-milk-tea_1.jpg',
    'Grilled Sandwich': 'foods/Grilled_Sandwich.jpg',
    'Veggie Pizza': 'foods/Veggie_Pizza.jpg',
}


def assign_menu_food_photos(apps, schema_editor):
    Food = apps.get_model('menu', 'Food')
    for name, image_path in FOOD_IMAGES.items():
        Food.objects.filter(name=name).filter(
            Q(image='') | Q(image__isnull=True) | Q(image__startswith='images/')
        ).update(image=image_path)


class Migration(migrations.Migration):

    dependencies = [
        ('menu', '0006_clear_legacy_image_paths'),
    ]

    operations = [
        migrations.RunPython(
            assign_menu_food_photos,
            migrations.RunPython.noop,
        ),
    ]
