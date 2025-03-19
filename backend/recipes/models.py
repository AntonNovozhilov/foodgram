from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Ingridients(models.Model):

    title = models.CharField(
        max_length=256, verbose_name="Название ингридиентов", unique=True
    )
    unit = models.CharField(
        max_length=15, verbose_name="Единица измерения", unique=True
    )

    class Meta:
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингридиенты'



class Tag(models.Model):

    title = models.CharField(max_length=256, verbose_name="Навзвание тэга")
    slug = models.SlugField(max_length=256,
                            verbose_name="Слаг",
                            auto_created=True
                        )
    
    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'


class Recipes(models.Model):

    Author = models.ForeignKey(User,
                               verbose_name="Автор",
                               on_delete=models.CASCADE
                            )
    title = models.CharField(
        max_length=256, verbose_name="Название рецепта", unique=True
    )
    image = models.ImageField(
        upload_to="images", verbose_name="Фотография блюда", unique=True
    )
    text = models.TextField(max_length=650, verbose_name="Описание рецепта")
    ingridients = models.ManyToManyField(Ingridients,
                                    verbose_name="Ингридиенты для рецепта",
                                    unique=True,
                                )
    tags = models.ManyToManyField(Tag,
                             verbose_name="Теги рецепта",
                             unique=True
                            )
    time = models.PositiveSmallIntegerField(
        verbose_name="Время приготовления в минутах", unique=True
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'