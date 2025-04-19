from api.api_v1.constants import MAX_VALIDATED, MIN_VALIDATED
from drf_extra_fields.fields import Base64ImageField
from recipes.models import (Ingredient, IngredientAmount, Recipe,
                            RecipeIngredient, Tags)
from rest_framework import serializers
from users.models import MyUser


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
        return obj.followers.filter(user=user).exists()


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
    amount = serializers.IntegerField(
        min_value=MIN_VALIDATED,
        max_value=MAX_VALIDATED
    )

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


class RecipeReadSerializer(serializers.ModelSerializer):
    """Чтение рецепта."""

    ingredients = IngredientInRecipeSerializer(
        many=True,
        source='amount_ingredient'
    )
    author = CustomUserSerializer(read_only=True)
    tags = TagSerializer(read_only=True, many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients',
            'is_favorited', 'is_in_shopping_cart',
            'name', 'image', 'text', 'cooking_time'
        )

    def get_is_favorited(self, obj):
        """Проверка, добавлен ли рецепт в избранное текущим пользователем."""
        user = self.context['request'].user
        return (
            not user.is_anonymous and obj.favorited_by.filter(
                user=user).exists())

    def get_is_in_shopping_cart(self, obj):
        """Добавление в список покупок."""
        user = self.context['request'].user
        return (not user.is_anonymous and obj.cart.filter(user=user).exists())


class RecipeWriteSerializer(serializers.ModelSerializer):
    """Запись рецепта."""

    ingredients = IngredientsinRecipeAmountSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tags.objects.all(),
        many=True
    )
    image = Base64ImageField()
    cooking_time = serializers.IntegerField(
        min_value=MIN_VALIDATED,
        max_value=MAX_VALIDATED
    )

    class Meta:
        model = Recipe
        fields = (
            'id', 'ingredients', 'tags', 'image', 'name',
            'text', 'cooking_time',
        )

    def validate_tags(self, tags):
        """Валидация тэгов."""
        tags_data = self.initial_data.get('tags')
        if tags_data is None:
            raise serializers.ValidationError('Нужен хотя бы один тег.')
        for tag_id in tags_data:
            if not Tags.objects.filter(id=tag_id).exists():
                raise serializers.ValidationError('Тег не существует.')
        return tags

    def validate_ingredients(self, ingredients):
        """Валидация."""
        if not ingredients:
            raise serializers.ValidationError('Нужен хотя бы один ингредиент.')
        seen = set()
        for item in ingredients:
            if item['id'].id in seen:
                raise serializers.ValidationError(
                    'Ингредиенты должны быть уникальны.')
            seen.add(item['id'].id)
        return ingredients

    def create_ingredients(self, ingredients, recipe):
        """Создание ингредиента."""
        ingredients_list = [IngredientAmount(
            recipe=recipe,
            ingredient=item['id'],
            amount=item['amount']
        ) for item in ingredients]
        IngredientAmount.objects.bulk_create(ingredients_list)

    def create(self, validated_data):
        """Создание рецепта."""
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
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
        validateds_tags = self.validate_tags(tags_data)
        instance.tags.set(validateds_tags)
        instance.amount_ingredient.all().delete()
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

    def validate(self, data):
        """Валдиация сериализатора."""
        user = self.context['request'].user
        following = data['following']
        if user == following:
            raise serializers.ValidationError("Нельзя подписаться на себя")
        if user.following_set.filter(pk=following.pk).exists():
            raise serializers.ValidationError("Вы уже подписаны")
        return data

    def get_is_subscribed(self, obj):
        """Проверка подписки."""
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return obj.followers.filter(user=user).exists()

    def get_recipes(self, obj):
        """Список рецептов подписанного пользователя."""
        queryset = obj.recipes.all()
        return RecipMiniSerializer(queryset, many=True).data

    def get_recipe_count(self, obj):
        """Количество рецептов."""
        return obj.recipes.count()
