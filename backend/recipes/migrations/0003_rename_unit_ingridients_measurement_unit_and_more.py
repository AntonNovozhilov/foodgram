# Generated by Django 4.2 on 2025-03-20 02:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='ingridients',
            old_name='unit',
            new_name='measurement_unit',
        ),
        migrations.RenameField(
            model_name='recipes',
            old_name='Author',
            new_name='author',
        ),
        migrations.RenameField(
            model_name='recipes',
            old_name='time',
            new_name='cooking_time',
        ),
        migrations.RenameField(
            model_name='recipes',
            old_name='ingridients',
            new_name='ingredients',
        ),
        migrations.RenameField(
            model_name='recipes',
            old_name='title',
            new_name='name',
        ),
        migrations.AddField(
            model_name='ingridients',
            name='amount',
            field=models.SmallIntegerField(default=1, verbose_name='Количество'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='recipes',
            name='is_favorited',
            field=models.BooleanField(default=False, verbose_name='В избранном'),
        ),
        migrations.AddField(
            model_name='recipes',
            name='is_in_shopping_cart',
            field=models.BooleanField(default=False, verbose_name='В избранном'),
        ),
        migrations.AlterField(
            model_name='tag',
            name='slug',
            field=models.SlugField(blank=True, max_length=256, unique=True, verbose_name='Слаг'),
        ),
    ]
