from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Recipe(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=1000)
    rate = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], default=3)