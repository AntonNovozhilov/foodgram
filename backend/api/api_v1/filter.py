from django_filters import rest_framework as filter

from users.models import MyUser
from recipes.models import Recipe


class RecipeFilter(filter.FilterSet):
    """Катомный фильтр для рецепта."""

    tags = filter.AllValuesMultipleFilter(field_name='tags__slug')
    author = filter.ModelChoiceFilter(queryset=MyUser.objects.all())
    is_favorited = filter.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = filter.BooleanFilter(method='filter_is_in_shopping_cart')

    class Meta:
        model = Recipe
        fields = ('author', 'tags',)

    def filter_is_favorited(self, queryset, name, value):
        """Фильтр по избранному."""
        if value and not self.request.user.is_anonymous:
            return queryset.filter(favorites__user=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        """Фильтр по списку покупок."""
        if value and not self.request.user.is_anonymous:
            return queryset.filter(cart__user=self.request.user)
        return queryset