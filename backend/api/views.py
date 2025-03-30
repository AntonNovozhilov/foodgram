from http import HTTPStatus

from django.http import FileResponse
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from api.serializers import FavoritsRecipesSerializer, IngridientsSerializer, MyUserSerializer, RecipesSerializers, SubscriberSerializer, TagSerializer, ShoppingCardSerializer
from users.models import MyUser, Subscriptions
from recipes.models import FavoritsRecipes, Ingridients, Recipes, ShoppingCard, Tag
from .mixins import IngridientsMixins, UserMixins
from backend.settings import ALLOWED_HOSTS, MEDIA_ROOT
import os


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

class FavoritsRecipesViewSet(viewsets.ModelViewSet):
    queryset = FavoritsRecipes.objects.all()
    serializer_class = FavoritsRecipesSerializer

class RecipesViewSet(viewsets.ModelViewSet):
    queryset = Recipes.objects.all()
    serializer_class = RecipesSerializers

    @action(detail=True, url_path='get-link')
    def link(self, request, pk=None):
        obj = get_object_or_404(Recipes, pk=pk)
        return Response({'short-link': f'https://{ALLOWED_HOSTS[0]}/recipes/{obj.id}/'})
    
    
    @action(detail=False, url_path='download_shopping_cart')
    def down_cart(self, request):
        user = request.user
        obj = ShoppingCard.objects.filter(user=user)
        ingredients_list = []
        for item in obj:
            for recipes in item:
                for ingridiets in recipes.ingredients.all():
                    ingredients_list.append(f'{ingridiets.titel} - {ingridiets.measurement_unit} - {ingridiets.amount}')
        file_text= os.path.join(MEDIA_ROOT, 'list_shopping_cart.txt')
        with open (file_text, 'w') as file:
            file.write('\n'.join(ingredients_list))
        return FileResponse(open(file_text, 'rb'), as_attachment=True, filename='list_shopping_cart.txt')
    
    @action(detail=True, methods=['post', 'delete'], url_path='shopping_cart')
    def post_recipes_shopp_cart(self, request, pk=None):
        recipes = get_object_or_404(Recipes, pk=pk)
        user = request.user
        shoppingcart = ShoppingCard.objects.filter(user=user, recipes=recipes)
        if request.method == 'POST':
            if shoppingcart.exists():
                return Response({'errors': 'Рецепт уже с писке покупок'}, status=HTTPStatus.BAD_REQUEST)
            new_entry = ShoppingCard.objects.create(user=user, recipes=recipes)
            serializer = ShoppingCardSerializer(new_entry)
            return Response(serializer.data, status=HTTPStatus.CREATED)
        if request.method == 'DELETE':
            if shoppingcart.exists():
                shoppingcart.delete()
                return Response({'detail': 'Рецепт успешно удален из списка покупок'}, status=HTTPStatus.OK)
            return Response({'detail': 'Рецепта нет в списке покупок'}, status=HTTPStatus.BAD_REQUEST)
        

    @action(detail=True, methods=['post', 'delete'], url_path='favorite')
    def post_recipes_favorite(self, request, pk=None):
        recipes = get_object_or_404(Recipes, pk=pk)
        user = request.user
        favorite = FavoritsRecipes.objects.filter(user=user, recipes=recipes)
        if request.method == 'POST':
            if favorite.exists():
                return Response({'errors': 'Рецепт уже в списке избранных'}, status=HTTPStatus.BAD_REQUEST)
            new_entry = FavoritsRecipes.objects.create(user=user, recipes=recipes)
            serializer = FavoritsRecipesSerializer(new_entry)
            return Response(serializer.data, status=HTTPStatus.CREATED)
        if request.method == 'DELETE':
            if favorite.exists():
                favorite.delete()
                return Response({'detail': 'Рецепт успешно удален из списка избранных'}, status=HTTPStatus.OK)
            return Response({'detail': 'Рецепта нет в списке избранных'}, status=HTTPStatus.BAD_REQUEST)



class ShoppingListViewSet(viewsets.ModelViewSet):
    queryset = ShoppingCard.objects.all()
    serializer_class = ShoppingCardSerializer

class IngridientsViewSet(IngridientsMixins):
    queryset = Ingridients.objects.all()
    serializer_class = IngridientsSerializer

class UserViewSet(UserMixins):
    queryset = MyUser.objects.all()
    serializer_class = MyUserSerializer

    @action(detail=False)
    def me(self, request):
        # obj = request.user
        # serializer = self.get_serializer(obj)
        # serializer = MyUserSerializer(obj)
        return Response(MyUserSerializer(request.user).data)
    
    @action(detail=False, url_path='me/avatar', methods=['put', 'delete'])
    def put_avatar(self, request):
        obj = request.user
        avatar = request.data.get('avatar')
        serializer = self.get_serializer(obj, data={ 'avatar': avatar}, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=HTTPStatus.OK)
        return Response(serializer.errors, status=HTTPStatus.BAD_REQUEST)
    
    @action(detail=False, url_path='me/set_password', methods=['post'])
    def post_password(self, request):
        obj = request.user
        new_password = request.data.get('new_password')
        current_password = request.data.get('current_password')
        if new_password != current_password:
            serializer = self.get_serializer(obj, data={'password': new_password}, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=HTTPStatus.NO_CONTENT)
            return Response(serializer.errors, status=HTTPStatus.BAD_REQUEST)
        return Response(serializer.errors, status=HTTPStatus.BAD_REQUEST)
    
    @action(detail=False, url_path='subscriptions')
    def list_sub(self, request):
        user = request.user
        queryset = MyUser.objects.filter(subscriptions__author=user)
        serializer = SubscriberSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['post', 'delete'])
    def subscribe(self, request):
        user = request.user
        author = get_object_or_404(MyUser, id=self.kwargs.get('id'))
        if request.method == 'POST':
            new_sub = Subscriptions.objects.create(author=author , subscription=user)
            serializer = SubscriberSerializer(new_sub, context={'request': request})
            return Response(serializer.data, status=HTTPStatus.CREATED)
        if request.method == 'DELETE':
            subscription = get_object_or_404(Subscriptions,
                                             user=user,
                                             author=author)
            subscription.delete()
            return Response(status=HTTPStatus.NO_CONTENT)


# class SubscriptionsViewSet(viewsets.ModelViewSet):
#     queryset = Subscriptions.objects.all()
#     serializer_class = SubscriberSerializer

#     @action(detail=False, url_path='subscriptions')
#     def list_sub(self, request):
#         queryset = Subscriptions.objects.filter(followings__subscription=self.request.user)
#         serializer = SubscriberSerializer(queryset, many=True)
#         return Response(serializer.data)



