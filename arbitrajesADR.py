# para ejecutar se necesita python3
# lo ejecutamos así: python3 arbitrajesADR.py [valor de CCL como parametro]

import sys                              # para utilizar los parametros de entrada
import requests                         # para la API
import json                             # para la API
import pandas                           # necesaria para armar la grilla que se imprime
from AutenticarIO import AutenticarIO   # clase para autenticar a la API de IOL

url_general = "https://api.invertironline.com/api/v2/Cotizaciones/acciones/Panel General/argentina"
url_adr = "https://api.invertironline.com/api/v2/Cotizaciones/adrs/argentina/estados_Unidos"
#url_paneles = "https://api.invertironline.com/api/v2/argentina/Titulos/Cotizacion/Paneles/Acciones"

# funcion que hace el pedido get a la api, le paso por parametro tipo para diferenciar si es del panel general o ADR
# recorro la lista de datos obtenidos por el get
# para cada dato, busco si está en mi lista de tickers y lo guardo si corresponde
# retorno un diccionario (ticker,valor)
def obtener_datos(tipo, url_pedido, access_token, tickers):
    dic = dict()
    datos = requests.get(url=url_pedido, headers={
        "Authorization":"Bearer " + access_token
    }).json()
    for dat in datos['titulos']:
        for tick in tickers:
            i = 1 if tipo == 'general' else 0
            if dat['simbolo'] == tick[i]:
                dic[dat['simbolo']] = dat['ultimoPrecio']
    return dic

# utilizo la clase autenticar para obtener el token para comunicarme con la API
autenticar = AutenticarIO()
autenticar.conexion()
access_token = autenticar.get_access_token()
# lista de ticker de acciones que quiero consultar
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

# llamo a la funcion para que obtenga los datos de la API, para mercado arg y para los ADR
diccionario_arg = obtener_datos('general', url_general, access_token, tickers)
diccionario_adr = obtener_datos('adr', url_adr, access_token, tickers)

# consulto la lista de parametros, si no hay ninguno, calculo el CCL actual
# si viene el valor por parametro lo utilizo
if len(sys.argv) > 1:
    ccl_promedio = float(sys.argv[1])
else:
    # calculo el ccl de las acciones que estan en la lista
    for simbolo in tickers:
        #if simbolo[0] in ('PAM','GGAL','BMA','YPF','TGS','TEO','CEPU','EDN','SUPV','BBAR','LOMA','CRESY','IRSA','IRCP'):
        if simbolo[0] in ('PAM','GGAL','BMA','YPF','TGS'):
            precio_arg = diccionario_arg[simbolo[1]]
            precio_adr = diccionario_adr[simbolo[0]]
            lista_ccl.append((precio_arg / precio_adr) * simbolo[2])
    ccl_promedio = (sum(lista_ccl)/len(lista_ccl))  #obtengo el CCL promedio

# para cada una de las acciones de la lista de tickers
# busco el precio correspondiente en local y adrs
# calculo el CCL de esa accion y el valor arbitrado
for simbolo in tickers:
    precio_arg = diccionario_arg[simbolo[1]]
    precio_adr = diccionario_adr[simbolo[0]]
    # el valor CCL se calcula: (Precio Local / Precio del ADR) * Factor de Conversión
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
# ordeno la planilla por el nombre del ticker y reseteo el index
planilla = planilla.sort_values('TICKER')
planilla = planilla.reset_index(drop=True)
print(planilla)
# no quiero el csv por ahora, lo dejo comentado
#planilla.to_csv('arbitrajes.csv', index=False)
