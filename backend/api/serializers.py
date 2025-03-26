from rest_framework import serializers
from drf_extra_fields import fields

from users.models import MyUser
from recipes.models import FavoritsRecipes, Ingridients, Recipes, ShoppingCard, Tag

# class Base64Serializer(serializers.ModelSerializer):
#     image = fields.Base64ImageField(required=False)

#     class Meta:
#         model = Recipes
#         fields = ('image',)

class IngridientsSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Ingridients
        fields = ('title', 'measurement_unit',)

class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('name', 'slug',)

class RecipesSerializers(serializers.ModelSerializer):
    image = fields.Base64ImageField(required=False)

    class Meta:
        model = Recipes
        fields = ('ingredients', 'tags', 'name', 'text', 'cooking_time', 'image', 'author',)

class FavoritsRecipesSerializer(serializers.ModelSerializer):

    class Meta:
        model = FavoritsRecipes
        fields = ('recipes',)

class ShoppingCardSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShoppingCard
        fields = ('recipes_in_card',)

class MyUserSerializer(serializers.ModelSerializer):
    avatar = fields.Base64ImageField(required=False)

    class Meta:
        model = MyUser
        fields = ('username', 'email', 'first_name', 'last_name', 'password', 'avatar', 'is_subscribed', 'recipes',)
        read_only_fields = ('is_subscribed', 'recipes',)


# class ShoppingCardSerializer(serializers.ModelSerializer):

#     class Meta:
#         model = ShoppingCard
#         fields = ('name', image, cooking_time, ingredients)
        
