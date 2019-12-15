release: python manage.py migrate
release: python manage.py generate_test_data
web: gunicorn RecipesSite.wsgi --log-file -