from django.contrib import admin

from .models import Favorite, Ingredient, Recipe, ShoppingCart, Tags


@admin.register(Ingredient)
class IngridietAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    fields = ('name', 'measurement_unit', 'amount')
    search_fields = ('name',)

@admin.register(Tags)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    fields = [('name', 'slug')]
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Recipe)
class RecipesAdmin(admin.ModelAdmin):
    list_display = ('name', 'author')
    search_fields = ('name', 'author__username')
    list_filter = ('tags',)
    readonly_fields = ('favorited_count',)

    def favorited_count(self, obj):
        return obj.author.recipes.filter(is_favorited=True).count()
    favorited_count.__name__ = 'Добавлений в избранное'
    
@admin.register(ShoppingCart)
class ShoppingCardAdmin(admin.ModelAdmin):
    list_display = ['recipe', 'user']

@admin.register(Favorite)
class FavoritsRecipesAdmin(admin.ModelAdmin):
    list_display = ['recipe', 'user']
    
    


