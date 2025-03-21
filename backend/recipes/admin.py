from django.contrib import admin

from .models import Ingridients, Recipes, Tag


@admin.register(Ingridients)
class IngridietAdmin(admin.ModelAdmin):
    list_display = ('title', 'measurement_unit')
    fields = [('title', 'measurement_unit', 'amount')]
    search_fields = ('title',)

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug')
    fields = [('title', 'slug')]
    prepopulated_fields = {'slug': ('title',)}

@admin.register(Recipes)
class RecipesAdmin(admin.ModelAdmin):
    list_display = ('name', 'author')
    search_fields = ('name', 'author__username')
    list_filter = ('tags',)
    readonly_fields = ('favorited_count',)

    def favorited_count(self, obj):
        return obj.author.recipes.filter(is_favorited=True).count()
    favorited_count.__name__ = 'Добавлений в избранное'
    
    
    
    


