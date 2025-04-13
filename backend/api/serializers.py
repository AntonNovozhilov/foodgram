from django.shortcuts import get_object_or_404
from rest_framework import serializers
from djoser.serializers import UserSerializer
from drf_extra_fields.fields import Base64ImageField

from users.models import Follow, MyUser
from recipes.models import Favorite, Ingredient, IngredientAmount, Recipe, RecipeIngredient, ShoppingCart, Tags


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


class IngredientsinRecipeAmountSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField()
    class Meta:
        model = IngredientAmount
        fields = ('id', 'amount')


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount',)


class RecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    tags = TagSerializer(read_only=True, many=True)
    author = UserSerializer(read_only=True)
    ingredients = IngredientsinRecipeAmountSerializer(
        many=True
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text',
                  'cooking_time')

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return obj.favorited_by.filter(user=user).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return obj.cart.filter(user=user).exists()
    


    def validate(self, data):
        ingredients = self.initial_data.get('ingredients')
        image = self.initial_data.get('image')
        tags_data = self.initial_data.get('tags')
        cooking_time = self.initial_data.get('cooking_time')
        if cooking_time < 1:
            raise serializers.ValidationError('Нужно время на готовку')
        if not  tags_data:
            raise serializers.ValidationError('Нужен хоть один тег')
        tags_list = []
        for tags in tags_data:
            tag = get_object_or_404(Tags, id=tags)
            if tag in tags_list:
                raise serializers.ValidationError('Тег должен быть уникальным')
            tags_list.append(tag)
        if not image:
            raise serializers.ValidationError('Поле картинки пустое')
        if not ingredients:
            raise serializers.ValidationError('Нужен хоть один ингридиент для рецепта')
        ingredient_list = []
        for ingredient_item in ingredients:
            ingredient = get_object_or_404(Ingredient,
                                           id=ingredient_item['id'])
            if ingredient in ingredient_list:
                raise serializers.ValidationError('Ингридиенты должны '
                                                  'быть уникальными')
            ingredient_list.append(ingredient)
            if int(ingredient_item['amount']) <= 0:
                raise serializers.ValidationError('Ингридиентов должено быть больше нуля')
        data['ingredients'] = ingredients
        return data

    def create_ingredients(self, ingredients, recipe):
        for ingredient in ingredients:
            IngredientAmount.objects.create(
                recipe=recipe,
                ingredient_id=ingredient.get('id'),
                amount=ingredient.get('amount'),
            )

    def create(self, validated_data):
        image = validated_data.pop('image')
        ingredients_data = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(image=image, **validated_data)
        tags_data = self.initial_data.get('tags')
        recipe.tags.set(tags_data)
        self.create_ingredients(ingredients_data, recipe)
        return recipe

    def update(self, instance, validated_data):
        instance.image = validated_data.get('image', instance.image)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )
        instance.tags.clear()
        tags_data = self.initial_data.get('tags')
        if tags_data is None:
                raise serializers.ValidationError('Нужен тег')
        instance.tags.set(tags_data)
        IngredientAmount.objects.filter(recipe=instance).all().delete()
        self.create_ingredients(validated_data.get('ingredients'), instance)
        instance.save()
        return instance


# class CropRecipeSerializer(serializers.ModelSerializer):
#     image = Base64ImageField()

#     class Meta:
#         model = Recipe
#         fields = ('id', 'name', 'image', 'cooking_time')
#         read_only_fields = ('id', 'name', 'image', 'cooking_time')

# class RecipeSerializer(serializers.ModelSerializer):
#     tags = TagSerializer(many=True)
#     author = serializers.SerializerMethodField()
#     ingredients = serializers.SerializerMethodField()
#     is_favorited = serializers.SerializerMethodField()
#     is_in_shopping_cart = serializers.SerializerMethodField()
    
#     class Meta:
#         model = Recipe
#         fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited', 'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time',)

#     def get_author(self, obj):
#         author = obj.author
#         return UserSerializer(author, context=self.context).data
    
#     def get_ingredients(self, obj):
#         ingredients = RecipeIngredient.objects.filter(recipe=obj)
#         return IngredientInRecipeSerializer(ingredients, many=True).data
    
#     def get_is_favorited(self, obj):
#         request = self.context.get('request')
#         if request.user.is_authenticated:
#             return obj.favorited_by.filter(user=request.user).exists()
#         return False
        
#     def get_is_in_shopping_cart(self, obj):
#         request = self.context.get('request')
#         if request.user.is_authenticated:
#             return obj.cart.filter(user=request.user).exists()
#         return False
    
# class IngredientsinRecipeAmountSerializer(serializers.ModelSerializer):
#     id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
#     amount = serializers.IntegerField()
#     class Meta:
#         model = IngredientAmount
#         fields = ('id', 'amount')


# class RecipeCreateSerializer(serializers.ModelSerializer):
#     tags = serializers.PrimaryKeyRelatedField(queryset=Tags.objects.all(), many=True)
#     ingredients = IngredientsinRecipeAmountSerializer(many=True)
#     image = Base64ImageField()

#     class Meta:
#         model = Recipe
#         fields = ('tags', 'ingredients', 'image', 'name', 'text', 'cooking_time', )

#     def create(self, validated_data):
#         ingredients_data = validated_data.pop('ingredients')
#         tags = validated_data.pop('tags')
        
#         request = self.context.get('request')
#         recipe = Recipe.objects.create(author=request.user, **validated_data)
#         recipe.tags.set(tags)
        
#         for item in ingredients_data:
#             RecipeIngredient.objects.create(
#                 recipe=recipe,
#                 ingredient=item['id'],
#                 amount=item['amount']
#             )
#         return recipe
    
#     # def to_representation(self, instance):
#     #     return RecipeSerializer(instance, context=self.context).data
    

# class RecipListShop(serializers.ModelSerializer):

#     class Meta:
#         model = Recipe
#         fields = ('name', 'image', 'cooking_time',)

# class BaseFaviriteAndShoppingCartSerializer(serializers.ModelSerializer):

#     class Meta:
#         fields = ('user', 'recipe')

# class FavoriteSerializer(BaseFaviriteAndShoppingCartSerializer):

#     class Meta(BaseFaviriteAndShoppingCartSerializer.Meta):
#         model = Favorite


# class ShoppingCartSerializer(BaseFaviriteAndShoppingCartSerializer):

#     class Meta(BaseFaviriteAndShoppingCartSerializer.Meta):
#         model = ShoppingCart