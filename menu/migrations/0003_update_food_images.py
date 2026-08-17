from django.db import migrations


def update_food_images(apps, schema_editor):
    Food = apps.get_model('menu', 'Food')
    updates = {
        'Cappuccino': 'images/cappuccino.jpg',
        'Classic Burger': 'images/burger.jpg',
        'Cheese Pizza': 'images/pizza.jpg',
        'Chocolate Cake': 'images/chocolate-cake.jpg',
        'Pasta': 'images/pasta.jpg',
        'Club Sandwich': 'images/sandwich.jpg',
        'French Fries': 'images/french-fries.jpg',
        'Cold Coffee': 'images/cold-coffee.jpg',
    }

    for name, image_path in updates.items():
        Food.objects.filter(name=name).update(image=image_path)


def revert_food_images(apps, schema_editor):
    Food = apps.get_model('menu', 'Food')
    revert = {
        'Cappuccino': 'images/cappuccino.svg',
        'Classic Burger': 'images/burger.svg',
        'Cheese Pizza': 'images/pizza.svg',
        'Chocolate Cake': 'images/cake.svg',
        'Pasta': '',
        'Club Sandwich': 'images/interior.svg',
        'French Fries': '',
        'Cold Coffee': 'images/barista.svg',
    }

    for name, image_path in revert.items():
        Food.objects.filter(name=name).update(image=image_path)


class Migration(migrations.Migration):

    dependencies = [
        ('menu', '0002_seed_food'),
    ]

    operations = [
        migrations.RunPython(update_food_images, revert_food_images),
    ]
