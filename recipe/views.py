from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Tag, Ingredient, Recipe
from recipe.serializers import TagSerializer, IngredientSerializer, RecipeSerializer, RecipeDetailSerializer

class BaseRecipeAttrViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin):
    """ Clase base """
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        """ Retornar objetos para el usuario autenticado """
        return self.queryset.filter(user=self.request.user).order_by('name')
    
    def perform_create(self, serializer):
        """ Creando nuevo ingrediente y tag """
        serializer.save(user=self.request.user)

class TagViewSet(BaseRecipeAttrViewSet):
    """ Manejar los tags en la base de datos """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

class IngredientViewSet(BaseRecipeAttrViewSet):
    """ Manejar los Ingredientes en la base de datos """
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer

class RecipeViewSet(viewsets.ModelViewSet):
    """ Manejar las recetas """
    serializer_class = RecipeSerializer
    queryset = Recipe.objects.all()
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        """ Retornar objetos para el usuario autenticado """
        return self.queryset.filter(user=self.request.user)

    def get_serializer_class(self):
        """ Retorna clase de serializador apropiada """
        if self.action == 'retrieve':
            return RecipeDetailSerializer
        
        return self.serializer_class

    def perform_create(self, serializer):
        """ Creando receta """
        serializer.save(user=self.request.user)