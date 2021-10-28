from user.serializers import UserSerializer, AuthTokenSerializer
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework import generics, authentication, permissions

from rest_framework.settings import api_settings

class CreateUserViews(generics.CreateAPIView):
    """ Crea un nuevo usuario en el sistema """
    serializer_class = UserSerializer

class CreateTokenView(ObtainAuthToken):
    """ Crear un nuevo auth token para el usuario """
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES

class ManageUserView(generics.RetrieveUpdateAPIView):
    """ Manejar el usuario autenticado """
    serializer_class = UserSerializer
    authentication_classes = (authentication.TokenAuthentication, )
    permission_classes = (permissions.IsAuthenticated, )

    def get_object(self):
        """ Obtener y retornar el usuario autenticado """
        return self.request.user