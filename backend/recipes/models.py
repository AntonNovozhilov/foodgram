from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()



class Tags(models.Model):
    '''Тэги.'''
    name = models.CharField(verbose_name='Название', max_length=100, unique=True)
    slug = models.SlugField(verbose_name='Слаг', max_length=100, unique=True)

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'


    def __str__(self):
        return f'{self.name}'
    
class Ingredient(models.Model):
    '''Ингрилиенты.'''
    name = models.CharField(verbose_name='Название', unique=True, max_length=150)
    measurement_unit = models.CharField(verbose_name='Единица измерения', max_length=10)

    class Meta:
        ordering = ['name']
        unique_together = ('name', 'measurement_unit')
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Инридиенты'
    
    def __str__(self):
        return f'{self.name} {self.measurement_unit}'
    
class Recipe(models.Model):
    '''Рецепты.'''
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recipes')
    name = models.CharField(max_length=200)
    image = models.ImageField(upload_to='recipes/images/')
    text = models.TextField()
    ingredients = models.ManyToManyField(Ingredient, through='RecipeIngredient')
    tags = models.ManyToManyField(Tags)
    cooking_time = models.PositiveSmallIntegerField()
    pub_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return f'{self.name}'

class RecipeIngredient(models.Model):
    '''Ингрилиенты в рецептах.'''
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='get_ingredients')
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, related_name='ingredients_in_recipe')
    amount = models.PositiveSmallIntegerField()

class Favorite(models.Model):
    '''Избранное.'''
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='favorited_by')

    class Meta:
        unique_together = ('user', 'recipe')
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'

class ShoppingCart(models.Model):
    '''Список покупок.'''
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='cart')

    class Meta:
        unique_together = ('user', 'recipe')
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'

class IngredientAmount(models.Model):
    '''Колво ингридиентов.'''
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, related_name='amount_ingredient',)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='amount_ingredient',)
    amount = models.PositiveSmallIntegerField(default=1)

    class Meta:
        verbose_name = 'Кол-во ингредиентов'
        verbose_name_plural = 'Кол-во ингредиентов'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_ingredient_in_recipe',
            )
        ]

    def __str__(self):
        return f'{self.ingredient} {self.recipe}'
