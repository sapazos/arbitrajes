# para ejecutar se necesita python3
# lo ejecutamos así: python3 arbitrajesADR.py
# podemos pasar el usuario y contraseña por parametro asi: python3 arbitrajesADR.py -u usuario -p password
# podemos pasarle un valor de CCL y que use ese en lugar de calcularlo: python3 arbitrajesADR.py -c 88.50

import argparse
import json                             # para leer el file de login por parametro
import requests                         # para la API
import pandas                           # necesaria para armar la grilla que se imprime
from AutenticarIO import AutenticarIO   # clase para autenticar a la API de IOL

url_general = "https://api.invertironline.com/api/v2/Cotizaciones/acciones/Panel General/argentina"
url_merval = "https://api.invertironline.com/api/v2/Cotizaciones/acciones/merval/argentina"
url_adr = "https://api.invertironline.com/api/v2/Cotizaciones/adrs/argentina/estados_Unidos"
url_bonos = "https://api.invertironline.com/api/v2/Cotizaciones/bonos/Soberanos en dólares/argentina"
url_cedears = "https://api.invertironline.com/api/v2/Cotizaciones/Acciones/CEDEARs/Argentina"
url_sp500 = "https://api.invertironline.com/api/v2/Cotizaciones/Acciones/SP500/Estados_Unidos"
#url_paneles = "https://api.invertironline.com/api/v2/argentina/Titulos/Cotizacion/Paneles/Acciones"

# --------------------------------------------------------------------------------------------------------------------------

# funcion que hace el pedido get a la api, le paso por parametro tipo para diferenciar si es del panel general o ADR
# recorro la lista de datos obtenidos por el get
# para cada dato, busco si está en mi lista de tickers y lo guardo si corresponde
# retorno un diccionario (ticker,valor)
def obtener_datos(posicion, url_pedido, access_token, tickers):
    dic = dict()
    datos = requests.get(url=url_pedido, headers={"Authorization":"Bearer " + access_token}).json()
    for dat in datos['titulos']:
        for tick in tickers:
            if posicion == 'primero' and dat['simbolo'] == tick[0]:
                dic[dat['simbolo']] = dat['ultimoPrecio']
            if posicion == 'segundo' and dat['simbolo'] == tick[1]:
                dic[dat['simbolo']] = dat['ultimoPrecio']
            if posicion == 'tercero' and dat['simbolo'] == tick[2]:
                dic[dat['simbolo']] = dat['ultimoPrecio']
    return dic

# --------------------------------------------------------------------------------------------------------------------------
# el valor CCL se calcula: (Precio Local / Precio del ADR) * Factor de Conversión
def calcular_arbitraje(tickers, diccionario_local, diccionario_afuera, diccionario_contado):
    lista_datos = []
    # para cada una de las acciones de la lista de tickers
    # busco el precio correspondiente en local y adrs
    # calculo el CCL de esa accion y el valor arbitrado
    for simbolo in tickers:
        precio_local = diccionario_local[simbolo[1]]
        precio_afuera = diccionario_afuera[simbolo[0]]
        if diccionario_contado != '':
            precio_contado = diccionario_contado[simbolo[2]]
            mep = round(float(precio_local / precio_afuera),2)     # redondeo y muestro la cotizacion con dos decimales
            ccl = round(float(precio_local / precio_contado),2)
        else:
            ccl = (precio_local / precio_afuera) * simbolo[2]
            arbitrado = (precio_afuera * ccl_promedio) / simbolo[2]
            diferencia = arbitrado - precio_local
            porcentaje = (1 - (precio_local / arbitrado)) * 100
        lista_ticker = []
        lista_ticker.append(simbolo[1]) # nombre ticker en argentina
        lista_ticker.append(precio_local)
        lista_ticker.append(precio_afuera)
        if diccionario_contado != '':
            lista_ticker.append(precio_contado)
            lista_ticker.append(mep)
        else:
            lista_ticker.append(simbolo[2]) # factor Conversión
            lista_ticker.append(round(arbitrado,2))
            lista_ticker.append(round(diferencia,2))
            lista_ticker.append(round(porcentaje,2))
        lista_ticker.append(round(ccl,2))
        lista_datos.append(lista_ticker)
    return lista_datos

# --------------------------------------------------------------------------------------------------------------------------

ccl_promedio = ''
user = ''
password = ''
parser = argparse.ArgumentParser()
parser.add_argument("-c", "--ccl", help="Valor de CCL fijo para calcular arbitrajes")
parser.add_argument("-f", "--file", help="ruta de archivo para login")
parser.add_argument("-u", "--user", help="Nombre de usuario de la API")
parser.add_argument("-p", "--password", help="Contraseña de usuario de la API")
args = parser.parse_args()
if args.ccl:
    ccl_promedio = float(args.ccl)
if args.file:
    archivo = args.file
    with open(archivo) as file:
        data = json.load(file)
        for datos in data['credenciales']:
            user = datos['user']
            password = datos['password']
if args.user:
    user = args.user
if args.password:
    password = args.password

# utilizo la clase autenticar para obtener el token para comunicarme con la API
autenticar = AutenticarIO()
try:
    autenticar.conexion(user, password)
except:
    print('Error de usuario o contraseña')
    exit()
access_token = autenticar.get_access_token()
#print(access_token)

# lista de ticker de acciones que quiero consultar
# ('LOMA','LOMA',5),
tickers_acciones = [('TEO','TECO2',5),('CEPU','CEPU',10),('GGAL','GGAL',10),('PAM','PAMP',25),
     ('TGS','TGSU2',5),('YPF','YPFD',1),('EDN','EDN',20),('BMA','BMA',10),('SUPV','SUPV',5),
     ('BBAR','BBAR',3),('CRESY','CRES',10),('IRS','IRSA',10),('IRCP','IRCP',4)]
#tickers_bonos = ['AA21','AA25','AA37','AA46','AL29','AL30','AL35','AL41','A2E8','AE38','GD29','GD30','GD35','GD38','GD41','GD46','AO20','AY24','DICA','PARA']
tickers_bonos = [('AL29D','AL29','AL29C'),('AL30D','AL30','AL30C'),('AL35D','AL35','AL35C'),
                ('AL41D','AL41','AL41C'),('AE38D','AE38','AE38C'),('GD29D','GD29','GD29C'),('GD30D','GD30','GD30C'),
                ('GD35D','GD35','GD35C'),('GD38D','GD38','GD38C'),('GD41D','GD41','GD41C'),('GD46D','GD46','GD46C')]
tickers_cedears = [('KO','KO',5),('MSFT','MSFT',10),('AAPL','AAPL',10),('AMZN','AMZN',144),('DIS','DISN',4)]

# llamo a la funcion para que obtenga los datos de la API, para mercado arg y para los ADR
diccionario_merval = obtener_datos('segundo', url_merval, access_token, tickers_acciones)
diccionario_general = obtener_datos('segundo', url_general, access_token, tickers_acciones)
diccionario_merval.update(diccionario_general)
diccionario_adr = obtener_datos('primero', url_adr, access_token, tickers_acciones)
# si el valor de CCL NO viene por parametro lo calculo
lista_ccl = []
if ccl_promedio == '':
    # calculo el ccl de las acciones que estan en la lista
    for simbolo in tickers_acciones:
        if simbolo[0] in ('PAM','GGAL','BMA','YPF','TGS'):
            precio_arg = diccionario_merval[simbolo[1]]
            precio_adr = diccionario_adr[simbolo[0]]
            lista_ccl.append((precio_arg / precio_adr) * simbolo[2])
    ccl_promedio = (sum(lista_ccl)/len(lista_ccl))  #obtengo el CCL promedio
lista_datos = calcular_arbitraje(tickers_acciones, diccionario_merval, diccionario_adr, '')
# armo la estructura que uso para el csv
planilla = pandas.DataFrame(lista_datos, columns=["TICKER","VALOR ARG","VALOR ADR","FACTOR","ARBITRADO","DIFERENCIA","PORCENTAJE","CCL"])
print ("CCL promedio: " + str(round(ccl_promedio,2)))
# ordeno la planilla por el nombre del ticker y reseteo el index
planilla = planilla.sort_values('PORCENTAJE')
planilla = planilla.reset_index(drop=True)
print(planilla)
# no quiero el csv por ahora, lo dejo comentado
# planilla.to_csv('arbitrajes.csv', index=False)

dic_p = obtener_datos('segundo', url_bonos, access_token, tickers_bonos)
dic_d = obtener_datos('primero', url_bonos, access_token, tickers_bonos)
dic_c = obtener_datos('tercero', url_bonos, access_token, tickers_bonos)
lista_datos = calcular_arbitraje(tickers_bonos, dic_p, dic_d, dic_c)
planilla = pandas.DataFrame(lista_datos, columns=["TICKER","VALOR ARG","VALOR DLR","VALOR CONT","MEP","CCL"])
print(planilla)

diccionario_cedears = obtener_datos('segundo', url_cedears, access_token, tickers_cedears)
diccionario_sp500 = obtener_datos('primero', url_sp500, access_token, tickers_cedears)
lista_datos = calcular_arbitraje(tickers_cedears, diccionario_cedears, diccionario_sp500, '')
# armo la estructura que uso para el csv
planilla = pandas.DataFrame(lista_datos, columns=["TICKER","VALOR CEDEAR","VALOR USA","FACTOR","ARBITRADO","DIFERENCIA","PORCENTAJE","CCL"])
# ordeno la planilla por el nombre del ticker y reseteo el index
planilla = planilla.sort_values('PORCENTAJE')
planilla = planilla.reset_index(drop=True)
print(planilla)
