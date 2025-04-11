from rest_framework import serializers
from djoser.serializers import UserSerializer
from drf_extra_fields import fields

from users.models import Follow, MyUser
from recipes.models import Favorite, Ingredient, Recipe, RecipeIngredient, ShoppingCart, Tags


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tags
        fields = ('name', 'slug',)

class IngtedienSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('name', 'measurement_unit',)


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    avatar = serializers.ImageField(read_only=True)

    class Meta:
        model = MyUser
        fields = ('id', 'email', 'username', 'first_name', 'last_name', 'is_subscribed', 'avatar')

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return Follow.objects.filter(user=user, following=obj).exists()


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    avatar = serializers.ImageField(read_only=True)

    class Meta:
        model = MyUser
        fields = ('id', 'email', 'username', 'first_name', 'last_name', 'password', 'avatar')

    def create(self, validated_data):
        user = MyUser.objects.create_user(**validated_data)
        return user
    
class UserAvatarAdd(serializers.ModelSerializer):
    avatar = fields.Base64ImageField()

    class Meta:
        model = MyUser
        fields = ('email', 'username', 'first_name', 'last_name', 'avatar',)

class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all(),)
    amount = serializers.IntegerField(min_value=1)

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount',)

class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    author = UserSerializer(read_only=True)
    ingredients = IngtedienSerializer(many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = fields.Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited', 'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time',)
        
    def get_is_favorited(self, obj):
        user = self.context['request'].user
        return obj.favorited_by.filter(user=user).exists()
    
    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        return obj.in_carts.filter(user=user).exists()
    

class FollowSerializer(UserSerializer):
    recipes = RecipeSerializer(many=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Follow
        fields = ('username', 'first_name', 'last_name', 'is_subscribed', 'recipes', 'recipes_count',)
    
    def get_recipes_count(self, obj):
        return obj.recipes.count()
    

class RecipListShop(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('name', 'image', 'cooking_time',)

class BaseFaviriteAndShoppingCartSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('user', 'recipe')

class FavoriteSerializer(BaseFaviriteAndShoppingCartSerializer):

    class Meta(BaseFaviriteAndShoppingCartSerializer.Meta):
        model = Favorite


class ShoppingCartSerializer(BaseFaviriteAndShoppingCartSerializer):

    class Meta(BaseFaviriteAndShoppingCartSerializer.Meta):
        model = ShoppingCart