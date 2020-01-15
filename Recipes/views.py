from rest_framework import status, filters
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.generics import ListAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from Recipes.models import Recipe, Ingredient, Category, Comment, Rating, User
from Recipes.serializer import RecipeSerializer, IngredientSerializer, CategorySerializer, CommentSerializer, \
    RatingSerializer, UserSerializer, DynamicRegistrationSerializer


class IndexView(APIView):

    def get(self, request):
        list_of_urls = ['recipes', 'recipes/<int:pk>', 'ingredients', 'categories', 'ratings', 'comments', 'users']
        return Response(list_of_urls, status=status.HTTP_200_OK)


class AuthTokenView(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({'id': user.id, 'token': token.key})


class AllRecipes(ListAPIView):
    permission_classes = (IsAuthenticated,)

    # queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer

    def get_queryset(self):
        queryset = Recipe.objects.all()
        amount = self.request.query_params.get('amount', None)
        if amount is None:
            return queryset.order_by('-creation_date')
        else:
            try:
                amount = int(amount)
            except ValueError:
                return queryset.order_by('-creation_date')
            return queryset.order_by('-creation_date')[:amount]

    def post(self, request, format=None):
        serializer = RecipeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RecipeView(RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer


class RecipeSearchView(ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = RecipeSerializer

    def get_queryset(self):
        params = self.request.query_params
        query = Recipe.objects.all()

        title = params.get('title', None)
        difficulty = params.get('difficulty', None)
        time = params.get('time', None)
        categories = params.get('categories', None)
        ingredients = params.get('ingredients', None)
        amount = params.get('amount', None)

        if title:
            query = query.filter(title__icontains=title)

        if difficulty and difficulty.isnumeric():
            query = query.filter(difficulty__lte=difficulty)

        if time and time.isnumeric():
            query = query.filter(time__lte=time)

        if categories:
            cat_list = categories.strip('[]')
            cat_list = set(cat_list.split(','))
            query = query.filter(categories__name__in=cat_list).distinct()

        if ingredients:
            ing_list = ingredients.strip('[]')
            ing_list = set(ing_list.split(','))
            query = query.filter(ingredients__name__in=ing_list).distinct()

        if amount and amount.isnumeric():
            query = query[:int(amount)]

        return query


class IngredientsView(ListAPIView):
    permission_classes = (IsAuthenticated,)

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['^name']

    def post(self, request):
        serializer = IngredientSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class IngredientView(RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated,)

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class CategoriesView(ListAPIView):
    permission_classes = (IsAuthenticated,)

    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    filter_backends = [filters.SearchFilter]
    search_fields = ['^name']

    def post(self, request):
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoryView(RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated,)

    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class CommentsView(ListAPIView):
    permission_classes = (IsAuthenticated,)

    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def post(self, request):
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RatingsView(ModelViewSet):
    permission_classes = (IsAuthenticated,)

    queryset = Rating.objects.all()
    serializer_class = RatingSerializer

    def create(self, request, *args, **kwargs):
        serializer = RatingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        Rating.objects.filter(user__nickname=data['user'], recipe=data['recipe']).delete()
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def get_queryset(self):
        queryset = Rating.objects.all()
        username = self.request.data.get('username', None)
        if username is not None:
            queryset = queryset.filter(user__nickname=username)
        user_id = self.request.data.get('user_id', None)
        if user_id is not None:
            queryset = queryset.filter(user__id=user_id)
        recipe = self.request.data.get('recipe_id', None)
        if recipe is not None:
            queryset = queryset.filter(recipe__id=recipe)
        return queryset


class UsersView(ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response("", status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserView(RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated,)

    queryset = User.objects.all()
    serializer_class = UserSerializer


class RegistrationValidationView(APIView):
    serializer_class = DynamicRegistrationSerializer

    def get(self, request):
        serializer = DynamicRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = User.objects.filter(basic_info__email=serializer.data['email'])
        return Response({'email': bool(user)}, status=status.HTTP_200_OK)
