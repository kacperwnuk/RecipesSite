import json
import os
from copy import copy
from datetime import datetime

from django.contrib.auth import get_user_model
from Recipes.models import User, Recipe, Category, Ingredient, Rating, Comment
from django.core.management.base import BaseCommand
import random

MODULE_PATH = os.path.dirname(__file__)
RECIPES_PATH = os.path.join(MODULE_PATH, 'recipes.json')
USERS_PATH = os.path.join(MODULE_PATH, 'users.json')
REPLACEMENTS_PATH = os.path.join(MODULE_PATH, 'replacements.json')
ACTIVITIES_PATH = os.path.join(MODULE_PATH, 'activities.json')

DEVELOPER_NICKNAME = 'developer'
DEVELOPER_PASSWORD = 'apsi-developer'
DEVELOPER_ACTIVE = True
SEED = 1
DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
RECIPES_FREQUENCIES = {
    0: 9,
    1: 4,
    2: 4,
    3: 1,
    4: 1,
    5: 1,
}
FAVOURITE_PER_USER = (0, 4)
ACTIVITY_PER_USER = (0, 3)  # ratings, comments etc.
RECIPES_DIFFICULTY = {
    ningr: diff
    for ningrs, diff in {(0, 6): 1, (7, 9): 2, (10, 11): 3, (12, 13): 4, (14, 36): 5}.items()
    for ningr in range(ningrs[0], ningrs[1] + 1)
}


class Command(BaseCommand):
    help = 'Populates database with test data.'

    def handle(self, *args, **options):
        random.seed(SEED)
        with open(RECIPES_PATH) as recipes_file:
            recipes = json.load(recipes_file)
            random.shuffle(recipes)
        with open(USERS_PATH) as users_file:
            users = json.load(users_file)
            random.shuffle(users)
        with open(ACTIVITIES_PATH) as activities_file:
            activities = json.load(activities_file)
            random.shuffle(activities)
        with open(REPLACEMENTS_PATH) as replacements_file:
            replacements = json.load(replacements_file)
            # random.shuffle(replacements)

        # users
        User.objects.exclude(nickname='developer').delete()
        get_user_model().objects.filter(is_superuser=False).exclude(username='developer').delete()
        django_users = []
        for user in users:
            new_user = User.objects.create(
                nickname=user['username'],
                bio='Lorem ipsum dolor sit amet, consectetur adipiscing elit, '
                    'sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. '
                    'Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi '
                    'ut aliquip ex ea commodo consequat.',
                basic_info=get_user_model().objects.create_user(
                    username=user['username'],
                    date_joined=datetime.strptime(user['date_joined'], DATETIME_FORMAT),
                    email=user['email'],
                    first_name=user['name'],
                    last_name=user['surname'],
                )
            )
            django_users.append(new_user)
            new_user.basic_info.set_password(DEVELOPER_PASSWORD)
            new_user.basic_info.save()

        if DEVELOPER_ACTIVE:
            if not User.objects.filter(nickname='developer'):
                new_user = User.objects.create(
                    nickname=DEVELOPER_NICKNAME,
                    bio='',
                    basic_info=get_user_model().objects.create_user(
                        username=DEVELOPER_NICKNAME,
                        email='developer@mail.com',
                        first_name='Apsi',
                        last_name='Developer',
                    )
                )
                new_user.basic_info.set_password(DEVELOPER_PASSWORD)
                new_user.basic_info.save()
        else:
            User.objects.filter(nickname='developer').delete()
            get_user_model().objects.filter(username='developer').delete()

        # recipes, ingredients, categories
        Ingredient.objects.all().delete()
        Recipe.objects.all().delete()
        Category.objects.all().delete()
        ingredients_mapping = {}
        categories_mapping = {}
        django_recipes = []
        for recipe in recipes:
            django_igredients = []
            for ingredient_name in recipe['ingredients']:
                if ingredient_name in ingredients_mapping:
                    django_igredients.append(ingredients_mapping[ingredient_name])
                else:
                    new_ingredient = Ingredient.objects.create(name=ingredient_name)
                    django_igredients.append(new_ingredient)
                    ingredients_mapping[ingredient_name] = new_ingredient

            django_categories = []
            for category_name in recipe['categories']:
                if category_name in categories_mapping:
                    django_categories.append(categories_mapping[category_name])
                else:
                    new_category = Category.objects.create(name=category_name)
                    django_categories.append(new_category)
                    categories_mapping[category_name] = new_category

            new_recipe = Recipe.objects.create(
                title=recipe['title'],
                description=recipe['instructions'],
                difficulty=RECIPES_DIFFICULTY.get(len(recipe['ingredients']), 3),
                time=random.randint(20, 150)
            )
            new_recipe.ingredients.set(django_igredients)
            new_recipe.categories.set(django_categories)
            django_recipes.append(new_recipe)

        # assign recipes to users
        current_user_pointer = 0
        current_recipe_pointer = 0
        for recipes_per_user, users_per_frequency in RECIPES_FREQUENCIES.items():
            for _ in range(users_per_frequency):
                for _ in range(recipes_per_user):
                    recipe = django_recipes[current_recipe_pointer]
                    user = django_users[current_user_pointer]
                    recipe.user = user
                    recipe.save()
                    current_recipe_pointer += 1
                current_user_pointer += 1

        for user in django_users:
            other_users_recipes = list(filter(lambda r: r.user != user, django_recipes))
            random.shuffle(other_users_recipes)
            favs = other_users_recipes[:random.randint(*FAVOURITE_PER_USER)]
            user.favourite_recipes.set(favs)

            other_users_recipes = set(other_users_recipes) - set(favs)
            recipes_with_activity = list(other_users_recipes)[:random.randint(*ACTIVITY_PER_USER)]
            for recipe in recipes_with_activity:
                activity = random.choice(activities)
                random_score = random.randint(*activity['rating'])
                Rating.objects.create(user=user, recipe=recipe, score=random_score)
                if activity['comment'] is not None:
                    Comment.objects.create(user=user, recipe=recipe, text=activity['comment'])

            user.save()

        # import networkx as nx
        # import matplotlib.pyplot as plt
        # g = nx.DiGraph()

        for group in replacements['full']:
            for ingredient_name in group:
                if ingredient_name not in ingredients_mapping:
                    ingredients_mapping[ingredient_name] = Ingredient.objects.create(
                        name=ingredient_name
                    )
                # g.add_node(ingredient_name)
            django_ingredient_group = [
                ingredients_mapping[ingredient_name]
                for ingredient_name in group
            ]
            for django_ingredient in django_ingredient_group:  # type: Ingredient
                for django_ingredient2 in django_ingredient_group:
                    if django_ingredient != django_ingredient2 and random.random() > 0.45:
                        django_ingredient.replacements.add(django_ingredient2)
                        # g.add_edge(django_ingredient.name, django_ingredient2.name)
                django_ingredient.save()

        for ingredient_name, ingredient_replacements in replacements['directed'].items():
            if ingredient_name not in ingredients_mapping:
                ingredients_mapping[ingredient_name] = Ingredient.objects.create(
                    name=ingredient_name
                )
            for replacement_name in ingredient_replacements:
                if replacement_name not in ingredients_mapping:
                    ingredients_mapping[replacement_name] = Ingredient.objects.create(
                        name=replacement_name
                    )
                ingr = ingredients_mapping[ingredient_name]
                repl = ingredients_mapping[replacement_name]
                ingr.replacements.add(repl)
                ingr.save()


        # nx.draw(g, with_labels=True, pos=nx.spring_layout(g, k=0.15, iterations=20))
        # plt.show()
