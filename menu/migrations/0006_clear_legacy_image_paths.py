from django.db import migrations


def clear_legacy_static_image_paths(apps, schema_editor):
    Food = apps.get_model('menu', 'Food')
    Food.objects.filter(image__startswith='images/').update(image='')


class Migration(migrations.Migration):

    dependencies = [
        ('menu', '0005_alter_food_price'),
    ]

    operations = [
        migrations.RunPython(
            clear_legacy_static_image_paths,
            migrations.RunPython.noop,
        ),
    ]
