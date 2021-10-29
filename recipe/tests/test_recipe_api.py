from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core.models import Recipe, Tag, Ingredient
from recipe.serializers import RecipeSerializer, RecipeDetailSerializer

import tempfile
import os
from PIL import Image

def image_upload_url(recipe_id):
    """ url de retorno de imagen subida """
    return reverse('recipe:recipe-upload-image', args=[recipe_id])

RECIPES_URL = reverse('recipe:recipe-list')

def sample_tag(user, name='Main course'):
    """ Crear y retornar tag """
    return Tag.objects.create(user=user, name=name)

def sample_ingredient(user, name='Main course'):
    """ Crear y retornar ingrediente """
    return Ingredient.objects.create(user=user, name=name)

def detail_recipe(recipe_id):
    """ Retorna receta detail url """
    return reverse('recipe:recipe-detail', args=[recipe_id])

def sample_recipe(user, **params):
    """ Crear y retornar receta """
    defaults = {
        'title':'Pizza',
        'time_minutes':20,
        'price':5.00
    }
    defaults.update(params)

    return Recipe.objects.create(user=user, **defaults)

class PublicRecipeApiTests(TestCase):
    """ Test acceso no autenticado al API """
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(email='test@datadosis.com', password='Testpass')
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        """ Probar obtener lista de recetas """
        sample_recipe(self.user)
        sample_recipe(self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.all().order_by('id')
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipes_limited_to_user(self):
        """ Probar obtener recetas para un usuario """
        user2 = get_user_model().objects.create_user(email='user2@user2.com', password='Testpass')
        sample_recipe(user2)
        sample_recipe(self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.filter(user=self.user).order_by('id')
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)

    def test_view_recipe_detail(self):
        """ Probar ver los detalles de una receta """
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        recipe.ingredients.add(sample_ingredient(user=self.user))

        url = detail_recipe(recipe.id)

        res = self.client.get(url)
        serializer = RecipeDetailSerializer(recipe)

        self.assertEqual(res.data, serializer.data)


    def test_create_basic_recipe(self):
        """ Prueba crear receta """
        payload = {
            'title':'Pizza',
            'time_minutes':20,
            'price':5.00
        }

        res = self.client.post(RECIPES_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id=res.data['id'])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(recipe, key))

    def test_create_recipe_with_tag(self):
        """ Prueba crear receta con tags """
        tag1 = sample_tag(self.user, 'tag 1')
        tag2 = sample_tag(self.user, 'tag 2')

        payload = {
            'title':'Pizza',
            'tags':[tag1.id, tag2.id],
            'time_minutes':20,
            'price':5.00
        }
        res = self.client.post(RECIPES_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id=res.data['id'])
        tags = recipe.tags.all()

        self.assertEqual(tags.count(), 2)
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

    def test_create_recipe_with_ingredient(self):
        """ Prueba crear receta con ingredientes """
        ingredient1 = sample_ingredient(self.user, 'ingredient 1')
        ingredient2 = sample_ingredient(self.user, 'ingredient 2')
        payload = {
            'title':'Pizza',
            'ingredients':[ingredient1.id, ingredient2.id],
            'time_minutes':20,
            'price':5.00
        }
        res = self.client.post(RECIPES_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        ingredients = recipe.ingredients.all()

        self.assertEqual(ingredients.count(), 2)
        self.assertIn(ingredient1, ingredients)
        self.assertIn(ingredient2, ingredients)

class RecipeImgaeUploadTests(TestCase):
    """  """
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user('test@test.com', 'testpass')
        self.client.force_authenticate(self.user)
        self.recipe = sample_recipe(user=self.user)
    
    def tearDown(self):
        self.recipe.image.delete()
    
    def test_upload_image_to_recipe(self):
        """ Probar subir imagen a receta """
        url = image_upload_url(self.recipe.id)
        with tempfile.NamedTemporaryFile(suffix='.jpg') as ntf:
            img = Image.new('RGB', (10, 10))
            img.save(ntf, format='JPEG')
            ntf.seek(0)
            res = self.client.post(url, {'image':ntf}, format='multipart')

        self.recipe.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('image', res.data)
        self.assertTrue(os.path.exists(self.recipe.image.path))

    def test_upload_image_bad_request(self):
        """ Probar subir imagen fallo """
        url = image_upload_url(self.recipe.id)
        res = self.client.post(url, {'image':'notimage'}, format='multipart')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)