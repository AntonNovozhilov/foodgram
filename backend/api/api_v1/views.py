from http import HTTPStatus

from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from recipes.models import (Ingredient, IngredientAmount, Recipe, ShoppingCart,
                            Tags)
from rest_framework import filters, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from users.models import Follow, MyUser

from .filter import RecipeFilter
from .pagination import CustomPagination
from .permissions import OwnerPermission
from .serializers import (CustomUserSerializer, FollowSerializer,
                          IngtedienSerializer, RecipeReadSerializer,
                          RecipeWriteSerializer, RecipMiniSerializer,
                          SetPasswordSerializer, TagSerializer, UserAvatarAdd,
                          UserCreateSerializer)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Тэги."""

    queryset = Tags.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = (IsAuthenticatedOrReadOnly,)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Ингредиенты."""

    queryset = Ingredient.objects.all()
    serializer_class = IngtedienSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)
    pagination_class = None


class UserViewSet(viewsets.ModelViewSet):
    """Пользователь."""

    queryset = MyUser.objects.all()
    pagination_class = CustomPagination

    def get_serializer_class(self):
        """Выбор сериализатора."""
        if self.action == 'create':
            return UserCreateSerializer
        return CustomUserSerializer

    @action(
        detail=False,
        methods=['post'],
        url_path='set_password',
        permission_classes=[OwnerPermission],
    )
    def set_password(self, request):
        """Смена пароля."""
        serializer = SetPasswordSerializer(
            data=request.data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response(
            {'status': 'Пароль успешно изменён'},
            status=HTTPStatus.NO_CONTENT
        )

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[OwnerPermission]
    )
    def me(self, request):
        """Получение своей карточки."""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(
        detail=False,
        methods=['put', 'delete'],
        url_path='me/avatar',
        permission_classes=[OwnerPermission],
    )
    def avatar(self, request):
        """Аватар пользователя."""
        user = request.user
        if request.method == 'DELETE':
            if user.avatar:
                user.avatar.delete()
            return Response(
                {'avatar': None},
                status=HTTPStatus.NO_CONTENT
            )
        if 'avatar' not in request.data:
            return Response(status=HTTPStatus.BAD_REQUEST)
        serializer = UserAvatarAdd(
            instance=user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'avatar': user.avatar.url}, status=HTTPStatus.OK)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
        """Подписки."""
        authors = Follow.objects.filter(user=request.user)
        result_page = self.paginate_queryset(authors)
        serializer = FollowSerializer(
            result_page, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, pk):
        """Подписаться, отписаться."""
        author = get_object_or_404(MyUser, id=pk)
        user = request.user
        if request.method == 'POST':
            follow = Follow.objects.create(user=user, following=author)
            serializer = FollowSerializer(
                follow, context={'request': request}
            )
            return Response(serializer.data, status=HTTPStatus.CREATED)
        if request.method == 'DELETE':
            follow = Follow.objects.filter(user=user, following=author)
            if follow.exists():
                follow.delete()
                return Response(status=HTTPStatus.NO_CONTENT)
            return Response(
                {'errors': 'Подписки нет'},
                status=HTTPStatus.BAD_REQUEST
            )

class RecipeViewSet(viewsets.ModelViewSet):
    """ViewSet для рецептов."""

    queryset = Recipe.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = PageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        """Выбор сериализатора."""
        if self.action in ('list', 'retrieve'):
            return RecipeReadSerializer
        return RecipeWriteSerializer

    def perform_create(self, serializer):
        """Создание рецепта."""
        serializer.save(author=self.request.user)

    def destroy(self, request, *args, **kwargs):
        """Удаление рецепта."""
        recipe = self.get_object()
        if recipe.author == request.user:
            recipe.delete()
            return Response(status=HTTPStatus.NO_CONTENT)
        return Response(status=HTTPStatus.FORBIDDEN)

    def partial_update(self, request, *args, **kwargs):
        """Обновление рецепта."""
        recipe = self.get_object()
        if recipe.author != request.user:
            return Response(status=HTTPStatus.FORBIDDEN)
        serializer = self.get_serializer(
            recipe, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=HTTPStatus.OK)

    @action(
        detail=True,
        url_path='get-link',
        permission_classes=[IsAuthenticatedOrReadOnly],
    )
    def get_link(self, request, pk=None):
        """Ссылка на рецепт."""
        recipe = get_object_or_404(Recipe, pk=pk)
        host = request.get_host()
        link = f'https://{host}/recipes/{recipe.id}/'
        return Response({'short-link': link}, status=HTTPStatus.OK)

    @action(
        detail=True,
        methods=['post', 'delete'],
        url_path='favorite',
        permission_classes=[IsAuthenticated],
    )
    def favorite(self, request, pk=None):
        """Добавить/удалить из избранного."""
        recipe = get_object_or_404(Recipe, pk=pk)
        user = request.user
        if request.method == 'POST':
            if user.favorites.filter(recipe=recipe).exists():
                return Response(
                    {'errors': 'Рецепт уже в избранном'},
                    status=HTTPStatus.BAD_REQUEST,
                )
            user.favorites.create(recipe=recipe)
            serializer = RecipMiniSerializer(
                recipe, context={'request': request}
            )
            return Response(serializer.data, status=HTTPStatus.CREATED)
        if request.method == 'DELETE':
            favorite = user.favorites.filter(recipe=recipe).first()
            if not favorite:
                return Response(
                    {'errors': 'Рецепта нет в избранном'},
                    status=HTTPStatus.BAD_REQUEST,
                )
            favorite.delete()
            return Response(status=HTTPStatus.NO_CONTENT)

    @action(
        detail=True,
        methods=['post', 'delete'],
        url_path='shopping_cart',
        permission_classes=[IsAuthenticated],
    )
    def shopping_cart(self, request, pk=None):
        """Добавить/удалить из списка покупок."""
        recipe = get_object_or_404(Recipe, pk=pk)
        user = request.user
        if request.method == 'POST':
            if user.cart.filter(recipe=recipe).exists():
                return Response(
                    {'errors': 'Рецепт уже в списке покупок'},
                    status=HTTPStatus.BAD_REQUEST,
                )
            ShoppingCart.objects.create(user=user, recipe=recipe)
            serializer = RecipMiniSerializer(
                recipe, context={'request': request}
            )
            return Response(serializer.data, status=HTTPStatus.CREATED)
        if request.method == 'DELETE':
            cart = user.cart.filter(recipe=recipe).first()
            if cart:
                cart.delete()
                return Response(status=HTTPStatus.NO_CONTENT)
            return Response(status=HTTPStatus.BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path='download_shopping_cart')
    def download_shopping_cart(self, request):
        """Скачать список покупок."""
        recipe_ids = request.user.cart.values_list('recipe__id', flat=True)
        ingredients = (
            IngredientAmount.objects.filter(recipe__id__in=recipe_ids)
            .values('ingredient__name', 'ingredient__measurement_unit')
            .annotate(amount=Sum('amount'))
            .order_by('ingredient__name')
        )
        content = ''
        for ing in ingredients:
            content += (
                f"{ing['ingredient__name']} — {ing['amount']} "
                f"{ing['ingredient__measurement_unit']}\n"
            )
        response = HttpResponse(content, content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment; filename="shopping_cart.txt"'
        )
        return response
