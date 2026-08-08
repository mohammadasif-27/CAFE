from django.db import migrations


def create_food_items(apps, schema_editor):
    Food = apps.get_model('menu', 'Food')
    sample_items = [
        {
            'name': 'Cappuccino',
            'description': 'Velvety espresso topped with silky steamed milk and latte art.',
            'category': 'Coffee',
            'price': '120.00',
            'image': 'images/cappuccino.svg',
            'available': True,
        },
        {
            'name': 'Classic Burger',
            'description': 'Juicy house-blend patty with crisp greens and creamy sauce.',
            'category': 'Burgers',
            'price': '150.00',
            'image': 'images/burger.svg',
            'available': True,
        },
        {
            'name': 'Cheese Pizza',
            'description': 'Wood-fired crust layered with melted cheese and fresh herbs.',
            'category': 'Pizza',
            'price': '200.00',
            'image': 'images/pizza.svg',
            'available': True,
        },
        {
            'name': 'Chocolate Cake',
            'description': 'Rich, moist cake with a creamy frosting finish.',
            'category': 'Desserts',
            'price': '100.00',
            'image': 'images/cake.svg',
            'available': True,
        },
        {
            'name': 'Almond Croissant',
            'description': 'Flaky pastry filled with almond cream and dusted with sugar.',
            'category': 'Breakfast',
            'price': '140.00',
            'image': 'images/croissant.svg',
            'available': True,
        },
        {
            'name': 'Espresso Shot',
            'description': 'Bold and aromatic espresso for a premium coffee boost.',
            'category': 'Coffee',
            'price': '80.00',
            'image': 'images/barista.svg',
            'available': True,
        },
        {
            'name': 'Grilled Sandwich',
            'description': 'Golden bread stuffed with melted cheese and fresh vegetables.',
            'category': 'Burgers',
            'price': '130.00',
            'image': 'images/interior.svg',
            'available': True,
        },
        {
            'name': 'Veggie Pizza',
            'description': 'Crisp vegetables and melted cheese on a perfectly baked crust.',
            'category': 'Pizza',
            'price': '180.00',
            'image': 'images/gallery-1.svg',
            'available': True,
        },
    ]

    for item in sample_items:
        Food.objects.get_or_create(name=item['name'], defaults=item)


def remove_food_items(apps, schema_editor):
    Food = apps.get_model('menu', 'Food')
    names = [
        'Cappuccino',
        'Classic Burger',
        'Cheese Pizza',
        'Chocolate Cake',
        'Almond Croissant',
        'Espresso Shot',
        'Grilled Sandwich',
        'Veggie Pizza',
    ]
    Food.objects.filter(name__in=names).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('menu', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_food_items, remove_food_items),
    ]
