from django.contrib import admin

from .models import Ingridients, Recipes, Tag


@admin.register(Ingridients)
class IngridietAdmin(admin.ModelAdmin):
    list_display = ('title', 'measurement_unit', 'amount')
    fields = [('title', 'measurement_unit', 'amount')]

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug')
    fields = [('title', 'slug')]
    prepopulated_fields = {'slug': ('title',)}

@admin.register(Recipes)
class RecipesAdmin(admin.ModelAdmin):
    list_display = ('author', 'name', 'text', 'cooking_time', 'is_favorited', 'is_in_shopping_cart')
    list_editable = ('name', 'cooking_time', 'is_favorited', 'is_in_shopping_cart')
    


