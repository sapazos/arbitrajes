# para ejecutar se necesita python3
# lo ejecutamos así: python3 arbitrajesADR.py

import sys
import requests
import json
import pandas
import getpass
from AutenticarIO import AutenticarIO

url_general = "https://api.invertironline.com/api/v2/Cotizaciones/acciones/Panel General/argentina"
url_adr = "https://api.invertironline.com/api/v2/Cotizaciones/adrs/argentina/estados_Unidos"
#url_paneles = "https://api.invertironline.com/api/v2/argentina/Titulos/Cotizacion/Paneles/Acciones"

def obtener_datos(tipo, url_pedido, access_token, tickers):
    dic = dict()
    datos = requests.get(url=url_pedido, headers={
        "Authorization":"Bearer " + access_token
    }).json()
    for titulo in datos['titulos']:
        for tick in tickers:
            i = 1 if tipo == 'general' else 0
            if titulo['simbolo'] == tick[i]:
                dic[titulo['simbolo']] = titulo['ultimoPrecio']
    return dic

autenticar = AutenticarIO()
autenticar.conexion()
access_token = autenticar.get_access_token()
# lista de ticker de bonos o acciones que quiero consultar
tickers = [('TEO','TECO2',5),('CEPU','CEPU',10),('GGAL','GGAL',10),('PAM','PAMP',25),
     ('TGS','TGSU2',5),('YPF','YPFD',1),('EDN','EDN',20),('BMA','BMA',10),('SUPV','SUPV',5),
     ('BBAR','BBAR',3),('LOMA','LOMA',5),('CRESY','CRES',10),('IRS','IRSA',10),('IRCP','IRCP',4)]
# defino listas que voy a utilizar para la salida csv
lista_nombre = []
lista_pesos = []
lista_dolares = []
lista_ccl = []
lista_datos = []
diccionario_arg = dict()
diccionario_adr = dict()
diccionario_arg = obtener_datos('general', url_general, access_token, tickers)
diccionario_adr = obtener_datos('adr', url_adr, access_token, tickers)
if len(sys.argv) > 1:
    ccl_promedio = float(sys.argv[1])
else:
    # Calculo el ccl de las acciones que estan en la lista
    for simbolo in tickers:
        if simbolo[0] in ('PAM','GGAL','BMA','YPF','TGS'):
            precio_arg = diccionario_arg[simbolo[1]]
            precio_adr = diccionario_adr[simbolo[0]]
            lista_ccl.append((precio_arg / precio_adr) * simbolo[2])
    ccl_promedio = (sum(lista_ccl)/len(lista_ccl))
for simbolo in tickers:
    precio_arg = diccionario_arg[simbolo[1]]
    precio_adr = diccionario_adr[simbolo[0]]
    #CCL = (Precio Local / Precio del ADR) * Factor de Conversión
    ccl = (precio_arg / precio_adr) * simbolo[2]
    arbitrado = (precio_adr * ccl_promedio) / simbolo[2]
    diferencia = arbitrado - precio_arg
    porcentaje = (1 - (precio_arg / arbitrado)) * 100
    lista_ticker = []
    lista_ticker.append(simbolo[1]) # nombre ticker en argentina
    lista_ticker.append(precio_arg)
    lista_ticker.append(precio_adr)
    lista_ticker.append(round(ccl,2))
    lista_ticker.append(simbolo[2]) # factor Conversión
    lista_ticker.append(round(arbitrado,2))
    lista_ticker.append(round(diferencia,2))
    lista_ticker.append(round(porcentaje,2))
    lista_datos.append(lista_ticker)

# armo la estructura que uso para el csv
planilla = pandas.DataFrame(lista_datos, columns=["TICKER","VALOR ARG","VALOR ADR","CCL","FACTOR","ARBITRADO","DIFERENCIA","PORCENTAJE"])
print ("CCL promedio: " + str(round(ccl_promedio,2)))
print (planilla)
# no quiero el csv por ahora, lo dejo comentado
#planilla.to_csv('arbitrajes.csv', index=False)
