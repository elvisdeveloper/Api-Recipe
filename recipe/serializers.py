from rest_framework import serializers

from core.models import Tag, Ingredient, Recipe

class TagSerializer(serializers.ModelSerializer):
    """ Serializador para objeto del Tag """
    class Meta:
        model = Tag
        fields = ('id', 'name')
        read_only_Fields = ('id',)

class IngredientSerializer(serializers.ModelSerializer):
    """ Serializador para objeto de los ingredinetes """
    class Meta:
        model = Ingredient
        fields = ('id', 'name')
        read_only_Fields = ('id',)

class RecipeSerializer(serializers.ModelSerializer):
    """ Serializador para objeto de los ingredientes """
    ingredients = serializers.PrimaryKeyRelatedField(many=True, queryset=Ingredient.objects.all())
    tags = serializers.PrimaryKeyRelatedField(many=True, queryset=Tag.objects.all())

    class Meta:
        model = Recipe
        fields = ('id','title', 'time_minutes', 'price', 'link', 'ingredients', 'tags')
        read_only_Fields = ('id',)

class RecipeDetailSerializer(RecipeSerializer):
    """ Serializar los detalles de una receta """
    ingredients = IngredientSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)

class RecipeImageSerializer(serializers.ModelSerializer):
    """ Serializar las imagenes """
    class Meta:
        model = Recipe
        fields = ('id','image')
        read_only_Fields = ('id',)

