import requests
import json
import getpass

# clase para autenticar en la API de IOL
# obtiene el token para hacer gets y puts en la API
class AutenticarIO:
    def __init__(self):
         self._url_token = "https://api.invertironline.com/token"
         self._access_token = 0
         self._refresh_token = 0

    def get_access_token(self):
        return self._access_token

    def __set_access_token(self, token):
        self._access_token = token

    def get_refresh_token(self):
        return self._refresh_token

    def __set_refresh_token(self, token):
        self._refresh_token = token

    def __pedir_token(self, data):
        respuesta = requests.post(url=self._url_token, data=data)
        return json.loads(respuesta.text)

    def conexion(self, user='', password=''):
        # Ingresa por consola el nombre y clave del broker
        if user == '':
            user = input("Ingresar el usuario: ")
            password = getpass.getpass("Ingresar la contraseña: ")
        data = {
            "username":user,
            "password":password,
            "grant_type":"password"
        }
        # llamo a la funcion que hace login y devuelve el token
        try:
            datos_token = self.__pedir_token(data)
            self.__set_access_token(datos_token['access_token'])      #token para acceder
            self.__set_refresh_token(datos_token['refresh_token'])    #token para refrescar, no lo uso en este script
        except:
            raise
