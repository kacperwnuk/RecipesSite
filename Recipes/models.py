from django.contrib.auth.models import User as BasicUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Avg


class User(models.Model):
    basic_info = models.OneToOneField(BasicUser, on_delete=models.CASCADE)
    nickname = models.CharField(max_length=100, unique=True)
    bio = models.TextField(max_length=1000, blank=True)
    favourite_recipes = models.ManyToManyField('Recipe', related_name='favourite_recipes', blank=True)
    # avatar = models.ImageField(upload_to='avatars/')

    def __str__(self):
        return self.nickname


class Ingredient(models.Model):
    name = models.CharField(max_length=100)
    replacements = models.ManyToManyField('Ingredient', blank=True)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=1000, blank=True)
    difficulty = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], default=3)
    creation_date = models.DateField(auto_now_add=True)
    time = models.IntegerField(validators=[MinValueValidator(1)], null=True)
    # photo = models.ImageField(upload_to='photos/')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    categories = models.ManyToManyField(Category, blank=True)
    ingredients = models.ManyToManyField(Ingredient)

    @property
    def rating(self):
        return self.rating_set.all().aggregate(Avg('score'))['score__avg'] or 'Recipe haven`t been rated yet.'

    @property
    def comments(self):
        return Comment.objects.filter(recipe=self)

    @property
    def number_of_comments(self):
        return Comment.objects.filter(recipe=self).count()

    @property
    def number_of_ratings(self):
        return Rating.objects.filter(recipe=self).count()

    def __str__(self):
        return self.title


class Comment(models.Model):
    text = models.TextField(max_length=300)
    creation_date = models.DateField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)


class Rating(models.Model):
    score = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
