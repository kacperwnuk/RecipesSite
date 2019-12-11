"""RecipesSite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path
from rest_framework_swagger.views import get_swagger_view
from rest_framework.authtoken.views import obtain_auth_token

import Recipes.views as recipe_views

schema_view = get_swagger_view(title='Pastebin API')


urlpatterns = [
    path('', schema_view),
    path('admin/', admin.site.urls),
    path('recipes', recipe_views.AllRecipes.as_view()),
    path('recipes/<int:pk>', recipe_views.RecipeView.as_view()),
    path('ingredients', recipe_views.IngredientsView.as_view()),
    path('categories', recipe_views.CategoriesView.as_view()),
    path('ratings', recipe_views.RatingsView.as_view()),
    path('comments', recipe_views.CommentsView.as_view()),
    path('users', recipe_views.UsersView.as_view()),
	path('auth', obtain_auth_token),

]
