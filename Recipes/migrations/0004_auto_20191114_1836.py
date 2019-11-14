# Generated by Django 2.2.7 on 2019-11-14 17:36

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Recipes', '0003_auto_20191114_1827'),
    ]

    operations = [
        migrations.RenameField(
            model_name='recipe',
            old_name='name',
            new_name='title',
        ),
        migrations.AddField(
            model_name='recipe',
            name='time',
            field=models.IntegerField(null=True, validators=[django.core.validators.MinValueValidator(1)]),
        ),
    ]