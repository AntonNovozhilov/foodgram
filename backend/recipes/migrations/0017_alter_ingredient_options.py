# Generated by Django 4.2 on 2025-04-15 04:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0016_ingredientamount_unique_ingredient_in_recipe'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='ingredient',
            options={'ordering': ['name'], 'verbose_name': 'Ингредиент', 'verbose_name_plural': 'Ингредиенты'},
        ),
    ]
