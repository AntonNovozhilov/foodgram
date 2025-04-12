from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()



class Tags(models.Model):
    name = models.CharField(verbose_name='Название', max_length=100, unique=True)
    slug = models.SlugField(verbose_name='Слаг', max_length=100, unique=True)

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'


    def __str__(self):
        return f'{self.name}'
    
class Ingredient(models.Model):
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
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='get_ingredients')
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, related_name='ingredients_in_recipe')
    amount = models.PositiveSmallIntegerField()

# class TagsinRecipe(models.Model):
#     recipes = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='tags')
#     tags = models.ForeignKey(Tags, on_delete=models.CASCADE, related_name='tags_in_recipe')

class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='favorited_by')

    class Meta:
        unique_together = ('user', 'recipe')
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'

class ShoppingCart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='cart')

    class Meta:
        unique_together = ('user', 'recipe')
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'

