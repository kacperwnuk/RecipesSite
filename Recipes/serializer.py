from rest_framework import serializers
from django.contrib.auth.models import User as BaseUser
from Recipes.models import Recipe, Ingredient, Category, Comment, Rating, User
from Recipes.recommender import propose_recipes


class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    """
    A ModelSerializer that takes an additional `fields` argument that
    controls which fields should be displayed.
    """

    def __init__(self, *args, **kwargs):

        fields = kwargs['context']['request'].query_params.get('fields', None)

        # Instantiate the superclass normally
        super(DynamicFieldsModelSerializer, self).__init__(*args, **kwargs)

        if fields:
            fields = fields.split(',')
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            existing = set(self.fields.keys())
            for field_name in existing - allowed:
                self.fields.pop(field_name)


class ReplacementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ['name']
        extra_kwargs = {
            'name': {'validators': []},
        }


class IngredientSerializer(serializers.ModelSerializer):
    replacements = ReplacementSerializer(many=True)

    # replacements = serializers.SlugRelatedField(many=True, slug_field='name', queryset=Ingredient.objects.all())

    class Meta:
        model = Ingredient
        fields = '__all__'
        extra_kwargs = {
            'name': {'validators': []},
        }

    def create(self, validated_data):
        replacements_data = validated_data.pop('replacements')
        ingredient = Ingredient.objects.create(**validated_data)
        for replacement_data in replacements_data:
            replacement = Ingredient.objects.create(**replacement_data)
            ingredient.replacements.add(replacement)
        return ingredient


class LimitedRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ['id', 'title', 'time']


class RecipeSerializer(DynamicFieldsModelSerializer, serializers.ModelSerializer):
    categories = serializers.SlugRelatedField(many=True, slug_field='name', queryset=Category.objects.all())
    # ingredients = serializers.SlugRelatedField(many=True, slug_field='name', queryset=Ingredient.objects.all())
    ingredients = IngredientSerializer(many=True)

    class Meta:
        model = Recipe
        fields = '__all__'

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        categories_data = validated_data.pop('categories')
        recipe = Recipe.objects.create(**validated_data)
        for ingredient_data in ingredients_data:
            replacements_data = ingredient_data.pop('replacements')
            ingredient = Ingredient.objects.create(recipe=recipe, **ingredient_data)
            for replacement_data in replacements_data:
                replacement = Ingredient.objects.create(**replacement_data)
                ingredient.replacements.add(replacement)
            recipe.ingredients.add(ingredient)
        # for category_data in categories_data:
        #     category = Category.objects.get(name=category_data['name'])
        #     recipe.categories.add(category)
        recipe.categories.add(*categories_data)  # slug related field stores list of objects
        recipe.save()
        return recipe


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
        extra_kwargs = {'password': {'write_only': True}}
        fields = ['username', 'password', 'email']


class UserSerializer(serializers.ModelSerializer):
    basic_info = BaseUserSerializer()
    favourite_recipes = LimitedRecipeSerializer(many=True)
    top_rated_recipes = serializers.SerializerMethodField()
    recommended_recipes = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = '__all__'

    def create(self, validated_data):
        basic_data = validated_data.pop('basic_info')
        favourite_recipes = validated_data.pop('favourite_recipes')
        base_user = BaseUser.objects.create_user(**basic_data)
        user = User.objects.create(basic_info=base_user, **validated_data)
        user.favourite_recipes.add(*favourite_recipes)
        return user

    def get_top_rated_recipes(self, user):
        ratings = Rating.objects.filter(user__pk=user.pk).order_by('-score')[:3]
        recipes = [rating.recipe for rating in ratings]
        serializer = LimitedRecipeSerializer(recipes, many=True)
        return serializer.data

    def get_recommended_recipes(self, user):
        recipes = propose_recipes(
            User.objects.prefetch_related('favourite_recipes').get(pk=user.pk).favourite_recipes.all(),
            Recipe.objects.prefetch_related('categories', 'ingredients'),
            list(Category.objects.all()), list(Ingredient.objects.all()))
        serializer = LimitedRecipeSerializer(recipes, many=True)
        return serializer.data
