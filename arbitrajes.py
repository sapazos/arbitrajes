# para ejecutar se necesita python3 y los import (pandas)
# pandas se utiliza para exportar los resultados a un csv, si no lo quieren hacer quiten el import pandas y la ultima línea del codigo
# lo ejecutamos así: python3 arbitrajes.py

import requests
import json
import pandas
from AutenticarIO import AutenticarIO

url_general = "https://api.invertironline.com/api/v2/Cotizaciones/bonos/Soberanos en dólares/argentina"

def obtener_datos(tipo, url_pedido, access_token, tickers):
    dic = dict()
    datos = requests.get(url=url_pedido, headers={
        "Authorization":"Bearer " + access_token
    }).json()
    for titulo in datos['titulos']:
        for tick in tickers:
            i = 'D' if tipo == 'dolares' else ''
            if titulo['simbolo'] == tick+i:
                dic[titulo['simbolo']] = titulo['ultimoPrecio']
    return dic

#Utilizamos la clase para autenticar a la API
autenticar = AutenticarIO()
autenticar.conexion()
access_token = autenticar.get_access_token()

# lista de ticker de bonos que quiero consultar
tickers = ['A2E2','A2E7','AA25','AA37','AC17','AO20','AY24','DICA','DICY','PARA','PARY']
# defino listas que voy a utilizar para la salida csv
listaNombre = []
listaValor = []
preplanilla = {}

dic_p = dict()
dic_p = obtener_datos('pesos', url_general, access_token, tickers)
dic_d = dict()
dic_d = obtener_datos('dolares', url_general, access_token, tickers)

# para cada ticker de la lista pido su cotizacion
for simbolo in tickers:
    precio_p = dic_p[simbolo]
    precio_d = dic_d[simbolo+'D']
    dolar = round(float(precio_p / precio_d),2)   # redondeo y muestro la cotizacion con dos decimales
    listaNombre.append(simbolo+'D')
    listaValor.append(dolar)

# armo la estructura que uso para el csv
preplanilla["TICKER"] = listaNombre
preplanilla["VALOR"] = listaValor
planilla = pandas.DataFrame(preplanilla, columns=["TICKER","VALOR"])
print (planilla)
# no quiero el csv por ahora, lo dejo comentado
#planilla.to_csv('arbitrajes.csv', index=False)
