from pprint import pprint

import numpy as np
from sklearn import neighbors as sn
from sklearn import preprocessing as sp

from Recipes.models import Recipe


def propose_recipes(user_recipes, recipes, categories: list, ingredients: list):
    # qs = Recipe.objects.values_list('title', 'difficulty', 'time', 'user', 'categories', 'ingredients').order_by('id')
    if not user_recipes:
        return []

    dataset, recipes_info = create_dataset(categories, ingredients, recipes)

    ids = find_user_recipes(recipes_info, user_recipes)
    user_recipes = dataset[ids]
    prediction_recipes = dataset

    # Scaling
    min_max_scaler = sp.MinMaxScaler()
    user_recipes = min_max_scaler.fit_transform(user_recipes)
    prediction_recipes = min_max_scaler.fit_transform(prediction_recipes)

    nbrs = sn.NearestNeighbors(n_neighbors=3, algorithm='brute').fit(prediction_recipes)
    dist, indices = nbrs.kneighbors(user_recipes)

    recommended_recipes = set()

    for neighbours, id in zip(indices, ids):
        # first neighbour is same recipe - dist = 0
        for neighbour in neighbours[1:]:
            recommended_recipes.add(Recipe.objects.get(pk=recipes_info[neighbour]))
    return recommended_recipes


def find_user_recipes(recipes_info, user_recipes):
    ids = []
    for recipe in user_recipes:
        for key, value in recipes_info.items():
            if value == recipe.pk:
                ids.append(key)
                break
    return ids


def create_dataset(categories, ingredients, recipes):
    category_size = len(categories)
    ingredients_size = len(ingredients)
    category_offset = 3
    ingredient_offset = category_offset + category_size

    fields = category_size + ingredients_size + category_offset
    dataset = np.zeros((recipes.count(), fields))

    recipes_info = {}
    for i, recipe in enumerate(recipes):
        recipes_info[i] = recipe.id
        dataset[i][0] = recipe.difficulty
        dataset[i][1] = recipe.time
        dataset[i][2] = recipe.user_id

        for category in recipe.categories.all():
            dataset[i, categories.index(category) + category_offset] = 1
        for ingredient in recipe.ingredients.all():
            dataset[i, ingredient_offset + ingredients.index(ingredient)] = 1

    return dataset, recipes_info
