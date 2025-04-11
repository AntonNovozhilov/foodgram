from django.db.models import Sum

from datetime import datetime
from http import HTTPStatus

from django.shortcuts import get_object_or_404
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend

from api.serializers import FavoriteSerializer, FollowSerializer, IngtedienSerializer, RecipListShop, RecipeSerializer, ShoppingCartSerializer, TagSerializer, UserAvatarAdd, UserCreateSerializer, UserSerializer
from api.permissions import IsAuthenticatedorCreate, OwnerPermission, IsAdminOrReadOnly
from .pagination import CustomPagination
from users.models import Follow, MyUser
from recipes.models import Favorite, Ingredient, Recipe, RecipeIngredient, ShoppingCart, Tags
from backend.settings import ALLOWED_HOSTS


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tags.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = (IsAdminOrReadOnly,)

class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngtedienSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)
    pagination_class = None

class UserViewSet(viewsets.ModelViewSet):
    queryset = MyUser.objects.all()
    pagination_class = CustomPagination

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer
    
    @action(detail=False, methods=['get'], permission_classes=[OwnerPermission])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(
        detail=False,
        methods=['put', 'post'],
        permission_classes=[OwnerPermission],
        url_path='set_password'
    )

    @action(detail=False, methods=['put', 'delete'], url_path='me/avatar', permission_classes=[OwnerPermission])
    def avatar(self, request):
        serializer = UserAvatarAdd(
            request.user,
            data=request.data,
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response({'avatar': request.user.avatar.url}, status=HTTPStatus.OK)
        return Response(serializer.errors, status=HTTPStatus.BAD_REQUEST)
    
    @action(detail=False, methods=['get'], permission_classes=IsAuthenticated)
    def subscriptions(self, request):
        serializer = FollowSerializer(many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['post', 'delete'], permission_classes=IsAuthenticated)
    def subscribe(self, request, pk):
        following = get_object_or_404(MyUser, pk=pk)
        user = request.user
        if request.method == 'POST':
            if following == user:
                return Response({'errors': 'Нельзя подписаться на себя'}, status=HTTPStatus.BAD_REQUEST)
            elif Follow.objects.filter(user=user, following=following).exists():
                return Response({'errors': 'Вы уже подписаны'}, status=HTTPStatus.BAD_REQUEST)
            else:
                Follow.objects.filter(user=user, following=following)
                serializer = FollowSerializer(following, context={'request': request})
                return Response(serializer.data, status=HTTPStatus.OK)
        if request.method == 'DELETE':
            serializer = Follow.objects.filter(user=user, following=following).exists()
            if serializer:
                serializer.delete()
                return Response(status=HTTPStatus.NO_CONTENT)
            else:
                return Response({'errors': 'Подписки нет'}, status=HTTPStatus.BAD_REQUEST)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = PageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('author', 'tags')

    @action(detail=False, url_name='get-link', permission_classes=[IsAuthenticated])
    def get_link(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        link = f'https://{ALLOWED_HOSTS[0]}/recipes/{recipe.id}/'
        return Response({'short-link': link}, status=HTTPStatus.OK)
    
    @staticmethod
    def add(request, serializer, pk):
        data = {
            'user': request.user.id,
            'recipe': pk
        }
        recipe = get_object_or_404(Recipe, pk=pk)
        serializer = serializer(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user, recipe=recipe)
        response = RecipListShop(
            Recipe.objects.get(pk=pk), context={'request': request}
        )
        return Response(response.data, status=HTTPStatus.CREATED)

    @staticmethod
    def remove(request, model, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        shoplist = model.objects.filter(user=request.user, recipe=recipe)
        if not shoplist:
            return Response(
                'Невозможно удалить рецепт из списка',
                status=HTTPStatus.BAD_REQUEST
            )
        shoplist.delete()
        return Response(status=HTTPStatus.NO_CONTENT)
    
    @action(detail=True, methods=['post'])
    def favorite(self, request, pk):\
        return self.add(request, FavoriteSerializer, pk)
    
    @favorite.mapping.delete
    def delete_from_favotite(self, request, pk):
        return self.remove(request, Favorite, pk)
    
    @action(detail=True, methods=['post'])
    def shopping_cart(self, request, pk):
        return self.add(request, ShoppingCartSerializer, pk)
    
    @shopping_cart.mapping.delete
    def delete_from_favotite(self, request, pk):
        return self.remove(request, ShoppingCart, pk)
    
    @action(detail=False, permission_classes=(IsAuthenticated))
    def download_shopping_cart(self, request):
        user = request.user
        if not user.shopping_cart.exists():
            return Response(status=HTTPStatus.BAD_REQUEST)

        ingredients = RecipeIngredient.objects.filter(
            cart__user=request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(amount=Sum('amount'))

        today = datetime.today()
        shopping_list = (
            f'Список покупок для: {user.get_full_name()}\n\n'
            f'Дата: {today:%Y-%m-%d}\n\n'
        )
        shopping_list += '\n'.join([
            f'- {ingredient["ingredient__name"]} '
            f'({ingredient["ingredient__measurement_unit"]})'
            f' - {ingredient["amount"]}'
            for ingredient in ingredients
        ])
        shopping_list += f'\n\nFoodgram ({today:%Y})'

        filename = f'{user.username}_shopping_list.txt'
        response = Response(shopping_list, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={filename}'

        return response