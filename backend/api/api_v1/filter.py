from django_filters import rest_framework as filter

from recipes.models import Recipe


class RecipeFilter(filter.FilterSet):
    tags = filter.CharFilter(field_name='tags__slug')
    author = filter.NumberFilter(field_name='author__id')

    class Meta:
        model = Recipe
        fields = ('author', 'tags',)