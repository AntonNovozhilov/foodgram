from http import HTTPStatus

from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination
from django_filters.rest_framework import DjangoFilterBackend

from api.serializers import (
    CustomUserSerializer,
    RecipMiniSerializer,
    FollowSerializer,
    IngtedienSerializer,
    RecipeSerializer,
    SetPasswordSerializer,
    TagSerializer,
    UserAvatarAdd,
    UserCreateSerializer,
)
from api.permissions import OwnerPermission
from users.models import Follow, MyUser
from recipes.models import (
    Favorite,
    Ingredient,
    IngredientAmount,
    Recipe,
    ShoppingCart,
    Tags
)
from backend.settings import ALLOWED_HOSTS
from .pagination import CustomPagination


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    '''Тэги.'''
    queryset = Tags.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = (IsAuthenticatedOrReadOnly,)

class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    '''Ингридиенты.'''
    queryset = Ingredient.objects.all()
    serializer_class = IngtedienSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)
    pagination_class = None

class UserViewSet(viewsets.ModelViewSet):
    '''Пользователь'''
    queryset = MyUser.objects.all()
    pagination_class = CustomPagination

    def get_serializer_class(self):
        '''Выбор сериализатора.'''
        if self.action == 'create':
            return UserCreateSerializer
        return CustomUserSerializer

    @action(detail=False, methods=['post'],
            url_path='set_password',
            permission_classes=[OwnerPermission]
            )
    def set_password(self, request):
        '''Смена пароля.'''
        serializer = SetPasswordSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response({'status': 'Пароль успешно изменён'}, status=HTTPStatus.NO_CONTENT)
    
    @action(detail=False, methods=['get'], permission_classes=[OwnerPermission])
    def me(self, request):
        '''Получение своей карточки.'''
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    

    @action(detail=False,
            methods=['put', 'delete'],
            url_path='me/avatar',
            permission_classes=[OwnerPermission]
            )
    def avatar(self, request):
        '''Аватар пользователя.'''
        user = request.user
        if request.method == 'DELETE':
            if user.avatar:
                user.avatar.delete()
            return Response({'avatar': None}, status=HTTPStatus.NO_CONTENT)
        else:
            if 'avatar' not in request.data:
                return Response(status=HTTPStatus.BAD_REQUEST)
            serializer = UserAvatarAdd(instance=user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({'avatar': user.avatar.url}, status=HTTPStatus.OK)
            return Response(serializer.errors, status=HTTPStatus.BAD_REQUEST)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        '''Подписки.'''
        authors = MyUser.objects.filter(followers__user=request.user)
        serializer = FollowSerializer(authors, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['post', 'delete'], permission_classes=[IsAuthenticated])
    def subscribe(self, request, pk):
        '''Подписаться, отписаться.'''
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
                return Response(serializer.data, status=HTTPStatus.CREATED)
        if request.method == 'DELETE':
            subscriber = Follow.objects.filter(user=user, following=following)
            if subscriber.exists():
                subscriber.delete()
                return Response(status=HTTPStatus.NO_CONTENT)
            else:
                return Response({'errors': 'Подписки нет'}, status=HTTPStatus.BAD_REQUEST)

class RecipeViewSet(viewsets.ModelViewSet):
    '''Рецепты.'''
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = LimitOffsetPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('author', 'tags__slug',)


    def perform_create(self, serializer):
        '''Создание.'''
        serializer.save(author=self.request.user)


    def destroy(self, request):
        '''Удаление.'''
        recipe = self.get_object()
        if recipe.author == request.user:
            recipe.delete()
            return Response(status=HTTPStatus.NOT_FOUND)
        return Response(status=HTTPStatus.FORBIDDEN)

    def partial_update(self, request, *args, **kwargs):
        '''Обновление.'''
        recipe = self.get_object()
        if recipe.author != request.user:
            return Response(status=HTTPStatus.FORBIDDEN)
        serializer = self.get_serializer(recipe, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=HTTPStatus.OK)
        


    @action(detail=True, url_path='get-link', permission_classes=[IsAuthenticatedOrReadOnly])
    def get_link(self, request, pk=None):
        '''Получение ссылки.'''
        recipe = get_object_or_404(Recipe, pk=pk)
        link = f'https://{ALLOWED_HOSTS[0]}/recipes/{recipe.id}/'
        return Response({'short-link': link}, status=HTTPStatus.OK)
    
    @action(detail=True, url_path='favorite', methods=['post', 'delete'], permission_classes=[IsAuthenticated])
    def favorite(self, request, pk=None):
        '''Добавление и удаление из избранного.'''
        recipe = get_object_or_404(Recipe, pk=pk)
        user = request.user
        if request.method == 'POST':
            if Favorite.objects.filter(user=user, recipe=recipe).exists():
                return Response('Рецеп уже в избранном', status=HTTPStatus.BAD_REQUEST)
            favorite = Favorite.objects.create(user=user, recipe=recipe)
            serializer = RecipMiniSerializer(recipe, context={'request': request})
            return Response(serializer.data, status=HTTPStatus.CREATED)
        elif request.method == 'DELETE':
            favorite = Favorite.objects.filter(user=user, recipe=recipe).first()
            if favorite:
                favorite.delete()
                return Response(status=HTTPStatus.NO_CONTENT)
            return Response(status=HTTPStatus.BAD_REQUEST)
        
    @action(detail=True, url_path='shopping_cart', methods=['post', 'delete'], permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        '''Список покупок.'''
        recipe = get_object_or_404(Recipe, pk=pk)
        user = request.user
        if request.method == 'POST':
            if ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
                return Response('Рецеп уже в списке покупок', status=HTTPStatus.BAD_REQUEST)
            shoppingcart = ShoppingCart.objects.create(user=user, recipe=recipe)
            serializer = RecipMiniSerializer(recipe, context={'request': request})
            return Response(serializer.data, status=HTTPStatus.CREATED)
        elif request.method == 'DELETE':
            shoppingcart = ShoppingCart.objects.filter(user=user, recipe=recipe).first()
            if shoppingcart:
                shoppingcart.delete()
                return Response(status=HTTPStatus.NO_CONTENT)
            return Response(status=HTTPStatus.BAD_REQUEST)
        
    @action(detail=False, methods=['get'], url_path='download_shopping_cart')
    def download_shopping_cart(self, request):
        '''Скачать список покупак.'''
        recipe_ids = request.user.cart.values_list('recipe__id', flat=True)
        ingredients = (
            IngredientAmount.objects
            .filter(recipe__id__in=recipe_ids)
            .values('ingredient__name', 'ingredient__measurement_unit')
            .annotate(amount=Sum('amount'))
            .order_by('ingredient__name')
        )
        content = ''
        for ing in ingredients:
            content += (
                f"{ing['ingredient__name']} — "
                f"{ing['amount']} {ing['ingredient__measurement_unit']}\n"
            )
        response = HttpResponse(content, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="shopping_cart.txt"'
        return response