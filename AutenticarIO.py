import requests
import json
import getpass

class AutenticarIO:
    def __init__(self):
         self._url_token = "https://api.invertironline.com/token"
         self._access_token = 0
         self._refresh_token = 0

    def get_access_token(self):
        return self._access_token

    def set_access_token(self, token):
        self._access_token = token

    def get_refresh_token(self):
        return self._refresh_token

    def set_refresh_token(self, token):
        self._refresh_token = token

    def pedir_token(self, data):
        respuesta = requests.post(url=self._url_token, data=data)
        return json.loads(respuesta.text)

    def conexion(self):
        # Ingresa por consola el nombre y clave del broker
        usuario = input("Ingresar el usuario: ")
        password = getpass.getpass("Ingresar la clave: ")
        data = {
            "username":usuario,
            "password":password,
            "grant_type":"password"
        }
        #llamo a la funcion que hace login y devuelve el token
        datos_token = self.pedir_token(data)
        self.set_access_token(datos_token['access_token'])      #token para acceder
        self.set_refresh_token(datos_token['refresh_token'])  #token para refrescar, no lo uso en este script
