from rest_framework import serializers
from django.contrib.auth.models import User as BaseUser
from Recipes.models import Recipe, Ingredient, Category, Comment, Rating, User


class IngredientSerializer(serializers.ModelSerializer):
    replacements = serializers.SlugRelatedField(many=True, slug_field='name', queryset=Ingredient.objects.all())

    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeSerializer(serializers.ModelSerializer):
    categories = serializers.SlugRelatedField(many=True, slug_field='name', queryset=Category.objects.all())
    ingredients = serializers.SlugRelatedField(many=True, slug_field='name', queryset=Ingredient.objects.all())
    # ingredients = IngredientSerializer(many=True)

    class Meta:
        model = Recipe
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class CommentSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(slug_field='nickname', queryset=User.objects.all())

    class Meta:
        model = Comment
        fields = '__all__'


class RatingSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(slug_field='nickname', queryset=User.objects.all())

    class Meta:
        model = Rating
        fields = '__all__'


class BaseUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = BaseUser
        fields = ['username', 'password', 'email']


class UserSerializer(serializers.ModelSerializer):
    basic_info = BaseUserSerializer()

    class Meta:
        model = User
        fields = '__all__'

    def create(self, validated_data):
        basic_data = validated_data.pop('basic_info')
        favourite_recipes = validated_data.pop('favourite_recipes')
        base_user = BaseUser.objects.create(**basic_data)
        user = User.objects.create(basic_info=base_user, **validated_data)
        user.favourite_recipes.add(*favourite_recipes)
        return user
