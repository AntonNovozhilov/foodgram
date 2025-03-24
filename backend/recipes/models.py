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

    name = models.CharField(max_length=256,
                             verbose_name="Уникальное название",
                             unique=True, blank=False, null=False
                            )
    slug = models.SlugField(max_length=256,
                            verbose_name="Уникальный слаг",
                            unique=True,
                            blank=False,
                            null=False
                        )
    
    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return f'{self.name} ({self.slug})'


class Recipes(models.Model):

    author = models.ForeignKey(User,
                               verbose_name="Автор",
                               on_delete=models.CASCADE,
                               blank=False,
                               related_name='recipes'
                            )
    name = models.CharField(max_length=256,
                             verbose_name="Название",
                             unique=True,
                             blank=False
                            )
    image = models.ImageField(upload_to="images",
                              verbose_name="Фотография блюда",
                              blank=False,
                              null=False
                            )
    text = models.TextField(max_length=650,
                            verbose_name="Описание",
                            blank=False,
                            null=False
                        )
    ingredients = models.ManyToManyField(Ingridients,
                                    verbose_name="Список ингредиентов",
                                    related_name='ingredients',
                                    blank=False,
                                )
    tags = models.ManyToManyField(Tag,
                             verbose_name="Список id тегов",
                             blank=False,
                             related_name='tags'
                            )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name="Время приготовления (в минутах)",
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
    
class FavoritsRecipes(models.Model):
    recipes = models.ForeignKey(Recipes,
                                on_delete=models.CASCADE,
                                related_name='recipes',
                                verbose_name='Рецепты')
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             verbose_name='Пользователь',
                             help_text='У какого пользователя рецепт в избраном'
                            )

    class Meta:
        verbose_name = 'Рецепт в избранном'
        verbose_name_plural = 'Рецепты в избранном'

    def __str__(self):
        return f'{self.recipes}'

    
class ShoppingCard(models.Model):
    recipes = models.ForeignKey(Recipes,
                                verbose_name='Рецепт',
                                on_delete=models.CASCADE,
                                related_name='recipes_in_card',
                                help_text='Какой рецепт надо добавить в список'
                            )
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             verbose_name='Пользователь',
                             help_text='Какому пользователю добавить рецепт в список покупок')
    
    class Meta:
        verbose_name = 'Список покупок для рецептов'
        verbose_name_plural = 'Списки покупок для рецептов'

    def __str__(self):
        return f'{self.recipes}'