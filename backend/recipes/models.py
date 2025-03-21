from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from backend.constants import MEASUREMENT_UNITS, TAGS

User = get_user_model()


class Ingridients(models.Model):

    title = models.CharField(
        max_length=256,
        verbose_name="Название ингридиентов",
        unique=True,
        blank=False,
        null=False
    )
    measurement_unit = models.CharField(
        max_length=15,
        verbose_name="Единица измерения",
        blank=False,
        null=False,
        choices=MEASUREMENT_UNITS
    )
    amount = models.SmallIntegerField(verbose_name='Количество',
                                      blank=False,
                                      null=False
                                    )

    class Meta:
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингридиенты'

    def __str__(self):
        return f'{self.title} {self.amount} {self.measurement_unit}'



class Tag(models.Model):

    title = models.CharField(max_length=256,
                             verbose_name="Название тэга",
                             unique=True, blank=False, null=False
                            )
    slug = models.SlugField(max_length=256,
                            verbose_name="Слаг",
                            unique=True,
                            blank=False,
                            null=False
                        )
    
    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return f'{self.title} ({self.slug})'


class Recipes(models.Model):

    author = models.ForeignKey(User,
                               verbose_name="Автор",
                               on_delete=models.CASCADE,
                               blank=False,
                               related_name='recipes'
                            )
    name = models.CharField(max_length=256,
                             verbose_name="Название рецепта",
                             unique=True,
                             blank=False
                            )
    image = models.ImageField(upload_to="images",
                              verbose_name="Фотография блюда",
                              blank=False,
                              null=False
                            )
    text = models.TextField(max_length=650,
                            verbose_name="Описание рецепта",
                            blank=False,
                            null=False
                        )
    ingredients = models.ManyToManyField(Ingridients,
                                    verbose_name="Ингридиенты для рецепта",
                                    blank=False,
                                )
    tags = models.ManyToManyField(Tag,
                             verbose_name="Теги рецепта",
                             blank=False,
                            )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name="Время приготовления в минутах",
        blank=False,
        null=False
    )
    is_favorited = models.BooleanField(default=False,
                                       verbose_name='В избранном'
                                    )
    is_in_shopping_cart = models.BooleanField(default=False,
                                              verbose_name='В списке покупок'
                                            )



    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return f'Рецепт {self.name}'