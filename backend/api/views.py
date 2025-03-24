from rest_framework import viewsets

from api.serializers import FavoritsRecipesSerializer, RecipesSerializers, TagSerializer
from recipes.models import FavoritsRecipes, Recipes, Tag


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

class FavoritsRecipesViewSet(viewsets.ModelViewSet):
    queryset = FavoritsRecipes.objects.all()
    serializer_class = FavoritsRecipesSerializer

class RecipesViewSet(viewsets.ModelViewSet):
    queryset = Recipes.objects.all()
    serializer_class = RecipesSerializers