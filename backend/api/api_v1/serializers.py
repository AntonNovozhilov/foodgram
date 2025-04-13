from django.shortcuts import get_object_or_404
from rest_framework import serializers
from djoser.serializers import UserSerializer
from drf_extra_fields.fields import Base64ImageField

from users.models import Follow, MyUser
from recipes.models import (
    Ingredient, IngredientAmount, Recipe,
    RecipeIngredient, Tags
)


class TagSerializer(serializers.ModelSerializer):
    """Теги."""

    class Meta:
        model = Tags
        fields = ('id', 'name', 'slug')


class IngtedienSerializer(serializers.ModelSerializer):
    """Ингредиенты."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')
        read_only_fields = ('id',)


class CustomUserSerializer(serializers.ModelSerializer):
    """Пользователь."""

    is_subscribed = serializers.SerializerMethodField()
    avatar = serializers.ImageField(read_only=True)

    class Meta:
        model = MyUser
        fields = (
            'id', 'email', 'username', 'first_name',
            'last_name', 'is_subscribed', 'avatar'
        )

    def get_is_subscribed(self, obj):
        """Проверка подписки."""
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return Follow.objects.filter(user=user, following=obj).exists()


class SetPasswordSerializer(serializers.Serializer):
    """Смена пароля."""

    new_password = serializers.CharField(required=True)
    current_password = serializers.CharField(required=True)

    def validate_current_password(self, value):
        """Проверка текущего пароля."""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Текущий пароль неверный.')
        return value

    def validate_new_password(self, value):
        """Проверка нового пароля."""
        return value

    def create(self, validated_data):
        """Метод-заглушка для сериализатора."""
        return validated_data


class UserCreateSerializer(serializers.ModelSerializer):
    """Регистрация пользователя."""

    password = serializers.CharField(write_only=True)

    class Meta:
        model = MyUser
        fields = (
            'id', 'email', 'username',
            'first_name', 'last_name', 'password'
        )

    def create(self, validated_data):
        """Создание пользователя."""
        return MyUser.objects.create_user(**validated_data)


class UserAvatarAdd(serializers.ModelSerializer):
    """Добавление аватара."""

    avatar = Base64ImageField()

    class Meta:
        model = MyUser
        fields = ('avatar',)


class IngredientsinRecipeAmountSerializer(serializers.ModelSerializer):
    """Количество ингредиентов."""

    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientAmount
        fields = ('id', 'amount')


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    """Ингредиенты в рецепте."""

    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    """Рецепт."""

    image = Base64ImageField()
    tags = TagSerializer(read_only=True, many=True)
    author = UserSerializer(read_only=True)
    ingredients = IngredientInRecipeSerializer(
        many=True,
        source='amount_ingredient'
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients',
            'is_favorited', 'is_in_shopping_cart',
            'name', 'image', 'text', 'cooking_time'
        )

    def get_is_favorited(self, obj):
        """Проверка избранного."""
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return obj.favorited_by.filter(user=user).exists()

    def get_is_in_shopping_cart(self, obj):
        """Проверка корзины."""
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return obj.cart.filter(user=user).exists()

    def validate(self, data):
        """Валидация рецепта."""
        ingredients = self.initial_data.get('ingredients')
        image = self.initial_data.get('image')
        tags_data = self.initial_data.get('tags')
        cooking_time = self.initial_data.get('cooking_time')

        if int(cooking_time) < 1:
            raise serializers.ValidationError('Нужно время на готовку.')
        if not tags_data:
            raise serializers.ValidationError('Нужен хотя бы один тег.')

        tags_list = []
        for tag_id in tags_data:
            tag = Tags.objects.filter(id=tag_id).first()
            if not tag:
                raise serializers.ValidationError('Тег не существует.')
            if tag in tags_list:
                raise serializers.ValidationError(
                    'Теги должны быть уникальны.')
            tags_list.append(tag)

        if not image:
            raise serializers.ValidationError('Картинка обязательна.')
        if not ingredients:
            raise serializers.ValidationError('Нужен хотя бы один ингредиент.')

        ingredient_list = []
        for item in ingredients:
            ingredient = get_object_or_404(Ingredient, id=item['id'])
            if ingredient in ingredient_list:
                raise serializers.ValidationError(
                    'Ингредиенты должны быть уникальны.')
            if int(item['amount']) <= 0:
                raise serializers.ValidationError(
                    'Количество должно быть больше 0.')
            ingredient_list.append(ingredient)

        data['ingredients'] = ingredients
        return data

    def create_ingredients(self, ingredients, recipe):
        """Создание ингредиентов."""
        for ingredient in ingredients:
            IngredientAmount.objects.create(
                recipe=recipe,
                ingredient_id=ingredient.get('id'),
                amount=ingredient.get('amount')
            )

    def create(self, validated_data):
        """Создание рецепта."""
        image = validated_data.pop('image')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(image=image, **validated_data)
        tags_data = self.initial_data.get('tags')
        recipe.tags.set(tags_data)
        self.create_ingredients(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        """Обновление рецепта."""
        instance.image = validated_data.get('image', instance.image)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )
        instance.tags.clear()
        tags_data = self.initial_data.get('tags')
        if tags_data is None:
            raise serializers.ValidationError('Нужен хотя бы один тег.')
        for tag_id in tags_data:
            if not Tags.objects.filter(id=tag_id).exists():
                raise serializers.ValidationError('Тег не существует.')
        instance.tags.set(tags_data)
        IngredientAmount.objects.filter(recipe=instance).delete()
        self.create_ingredients(validated_data.get('ingredients'), instance)
        instance.save()
        return instance


class RecipMiniSerializer(serializers.ModelSerializer):
    """Усечённый рецепт."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FollowSerializer(serializers.ModelSerializer):
    """Подписки."""

    recipes = serializers.SerializerMethodField()
    recipe_count = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = MyUser
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipe_count', 'avatar'
        )

    def get_is_subscribed(self, obj):
        """Проверка подписки."""
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return Follow.objects.filter(user=user, following=obj).exists()

    def get_recipes(self, obj):
        """Список рецептов подписанного пользователя."""
        queryset = obj.recipes.all()
        return RecipMiniSerializer(queryset, many=True).data

    def get_recipe_count(self, obj):
        """Количество рецептов."""
        return obj.recipes.count()
