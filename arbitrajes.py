# para ejecutar se necesita python3 y los import (pandas)
# pandas se utiliza para exportar los resultados a un csv, si no lo quieren hacer quiten el import pandas y la ultima línea del codigo
# lo ejecutamos así: python3 arbitrajes.py
# le doy el credito a facundo https://github.com/facundo-bogado/cursoTA y sus videos en youtube que me ayudaron a empezar con la api de IOL

import requests
import json
import pandas
import getpass

def pedir_token(data):
    url_token = "https://api.invertironline.com/token"
    respuesta = requests.post(url=url_token, data=data)
    return json.loads(respuesta.text)

# Ingresa por consola el nombre y clave del broker
usuario = input("Ingresar el usuario: ")
password = getpass.getpass("Ingresar la clave: ")
data = {
    "username":usuario,
    "password":password,
    "grant_type":"password"
}
#llamo a la funcion que hace login y devuelve el token
datos_token = pedir_token(data)
access_token = datos_token['access_token']      #token para acceder
refresh_token = datos_token['refresh_token']    #token para refrescar, no lo uso en este script

# lista de ticker de bonos o acciones que quiero consultar
tickers = ['A2E2','A2E7','AA25','AA37','AC17','AO20','AY24','DICA','DICY','PARA','PARY']
# defino listas que voy a utilizar para la salida csv
listaNombre = []
listaValor = []
preplanilla = {}
# para cada ticker de la lista pido su cotizacion
for simbolo in tickers:
    # consulto el ticker en pesos
    url_pedido = "https://api.invertironline.com/api/v2/bCBA/Titulos/"+simbolo+"/Cotizacion"
    datos = requests.get(url=url_pedido, headers={
        "Authorization":"Bearer " + access_token
    }).json()
    # me da las 5 puntas, solo voy a consultar la primera
    puntas = datos['puntas']
    precioP = puntas[0]['precioVenta']  # precio de venta en pesos
    # consulto el tiker en dolares +D
    url_pedido = "https://api.invertironline.com/api/v2/bCBA/Titulos/"+simbolo+"D/Cotizacion"
    datos = requests.get(url=url_pedido, headers={
        "Authorization":"Bearer " + access_token
    }).json()
    puntas = datos['puntas']
    precioD = puntas[0]['precioCompra']  # precio de compra en dolares
    # Nunca dividir por cero!
    if precioD > 0:
        dolar = round(float(precioP / precioD),2)   # redondeo y muestro la cotizacion con dos decimales
    else:
        dolar = 0
    print (str(simbolo+'D') + ': ' + str(dolar))
    listaNombre.append(simbolo+'D')
    listaValor.append(dolar)

# armo la estructura que uso para el csv
preplanilla["TICKER"] = listaNombre
preplanilla["VALOR"] = listaValor
planilla = pandas.DataFrame(preplanilla, columns=["TICKER","VALOR"])
# no quiero el csv por ahora, lo dejo comentado
#planilla.to_csv('arbitrajes.csv', index=False)
