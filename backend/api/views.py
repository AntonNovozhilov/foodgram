from http import HTTPStatus

from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from api.serializers import FavoritsRecipesSerializer, MyUserSerializer, RecipesSerializers, TagSerializer
from users.models import MyUser
from recipes.models import FavoritsRecipes, Recipes, ShoppingCard, Tag
from .mixins import UserMixins
from backend.settings import ALLOWED_HOSTS


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
    
    # @action(detail=True, methods=['get','post', 'delete'], url_path='shopping_cart')
    # def shopp_list(self, request):

# class ShoppingListViewSet(viewsets.ModelViewSet):
#     queryset = ShoppingCard
#     serializer_class = ()

    

class UserViewSet(UserMixins):
    queryset = MyUser.objects.all()
    serializer_class = MyUserSerializer

    @action(detail=False)
    def me(self, request):
        obj = request.user
        serializer = self.get_serializer(obj)
        return Response(serializer.data)
    
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


