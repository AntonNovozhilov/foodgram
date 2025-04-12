from rest_framework import serializers
from djoser.serializers import UserSerializer
from drf_extra_fields.fields import Base64ImageField

from users.models import Follow, MyUser
from recipes.models import Favorite, Ingredient, Recipe, RecipeIngredient, ShoppingCart, Tags


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tags
        fields = ('id', 'name', 'slug',)

class IngtedienSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit',)
        read_only = ('id',)


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
    
class SetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(required=True)
    current_password = serializers.CharField(required=True)

    def validate_current_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Текущий пароль не верный')
        return value
    
    def validate_new_password(self, value):
        if self.context['request'].user == value:
            raise serializers.ValidationError("Новый пароль не должен совпадать с текущим")
        return value




class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = MyUser
        fields = ('id', 'email', 'username', 'first_name', 'last_name', 'password',)

    def create(self, validated_data):
        user = MyUser.objects.create_user(**validated_data)
        return user
    
class UserAvatarAdd(serializers.ModelSerializer):
    avatar = Base64ImageField()

    class Meta:
        model = MyUser
        fields = ('avatar',)

class IngredientInRecipeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount',)

class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    author = serializers.SerializerMethodField()
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    
    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited', 'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time',)

    def get_author(self, obj):
        author = obj.author
        return UserSerializer(author, context=self.context).data
    
    def get_ingredients(self, obj):
        ingredients = RecipeIngredient.objects.filter(recipe=obj)
        return IngredientInRecipeSerializer(ingredients, many=True).data
    
    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request.user.is_authenticated:
            return obj.favorited_by.filter(user=request.user).exists()
        return False
        
    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request.user.is_authenticated:
            return obj.cart.filter(user=request.user).exists()
        return False
    

# class RecipeCreateSerializer(RecipeSerializer):
#     author = serializers.SerializerMethodField()

#     class Meta(RecipeSerializer):

#     def get_author(self, request):
#         return request.user
# class RecipeIngredientSerializer(serializers.ModelSerializer):
#     id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all(),)
#     amount = serializers.IntegerField(min_value=1)

#     class Meta:
#         model = RecipeIngredient
#         fields = ('id', 'amount',)

# class RecipeSerializer(serializers.ModelSerializer):
#     tags = TagSerializer(many=True)
#     author = UserSerializer(read_only=True)
#     ingredients = IngtedienSerializer(many=True)
#     is_favorited = serializers.SerializerMethodField()
#     is_in_shopping_cart = serializers.SerializerMethodField()
#     image = Base64ImageField()

#     class Meta:
#         model = Recipe
#         fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited', 'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time',)
        
#     def get_is_favorited(self, obj):
#         user = self.context['request'].user
#         return obj.favorited_by.filter(user=user).exists()
    
#     def get_is_in_shopping_cart(self, obj):
#         user = self.context['request'].user
#         return obj.in_carts.filter(user=user).exists()
    
class RecipeCreateSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(queryset=Tags.objects.all(), many=True)
    ingredients = IngredientInRecipeSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('tags', 'ingredients', 'image', 'name', 'text', 'cooking_time', )

    def add_ingredients_and_tags(self, tags, ingredients, recipe):
        for tag in tags:
            recipe.tags.add(tag)
            recipe.save()
        for ingredient in ingredients:
            IngredientInRecipeSerializer.objects.create(
                id=ingredient.get('id'),
                amount=ingredient.get('amount'),
                recipe=recipe
            )
        return recipe
    
    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        return self.add_ingredients_and_tags(tags, ingredients, recipe)
    

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