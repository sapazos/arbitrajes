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
            if tipo == 'general' and dat['simbolo'] == tick[1]:
                dic[dat['simbolo']] = dat['ultimoPrecio']
            if tipo == 'adr' and dat['simbolo'] == tick[0]:
                dic[dat['simbolo']] = dat['ultimoPrecio']
            if tipo == 'dolares' and dat['simbolo'] == tick+'D':
                dic[dat['simbolo']] = dat['ultimoPrecio']
            if tipo == 'pesos' and dat['simbolo'] == tick:
                dic[dat['simbolo']] = dat['ultimoPrecio']
    return dic

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

# lista de ticker de acciones que quiero consultar
# ('LOMA','LOMA',5),
tickers = [('TEO','TECO2',5),('CEPU','CEPU',10),('GGAL','GGAL',10),('PAM','PAMP',25),
     ('TGS','TGSU2',5),('YPF','YPFD',1),('EDN','EDN',20),('BMA','BMA',10),('SUPV','SUPV',5),
     ('BBAR','BBAR',3),('CRESY','CRES',10),('IRS','IRSA',10),('IRCP','IRCP',4)]
tickers_bonos = ['AA21','AA25','AA37','AA46','AL29','AL30','AL35','AL41','A2E8','AE38','GD29','GD30','GD35','GD38','GD41','GD46','AO20','AY24','DICA','PARA']
# defino listas que voy a utilizar para la salida csv
lista_ccl = []
lista_datos = []
diccionario_arg = dict()
diccionario_arg_g = dict()
diccionario_adr = dict()

# llamo a la funcion para que obtenga los datos de la API, para mercado arg y para los ADR
diccionario_arg = obtener_datos('general', url_merval, access_token, tickers)
diccionario_arg_g = obtener_datos('general', url_general, access_token, tickers)
diccionario_arg.update(diccionario_arg_g)
diccionario_adr = obtener_datos('adr', url_adr, access_token, tickers)
# si el valor de CCL NO viene por parametro lo calculo
if ccl_promedio == '':
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
planilla = planilla.sort_values('PORCENTAJE')
planilla = planilla.reset_index(drop=True)
print(planilla)
# no quiero el csv por ahora, lo dejo comentado
# planilla.to_csv('arbitrajes.csv', index=False)

lista_nombre = []
lista_mep = []
lista_datos = []
dic_p = dict()
dic_d = dict()

dic_p = obtener_datos('pesos', url_bonos, access_token, tickers_bonos)
dic_d = obtener_datos('dolares', url_bonos, access_token, tickers_bonos)
# para cada ticker de la lista pido su cotizacion
for simbolo in tickers_bonos:
    precio_p = dic_p[simbolo]
    precio_d = dic_d[simbolo+'D']
    dolar = round(float(precio_p / precio_d),2)     # redondeo y muestro la cotizacion con dos decimales
    lista_mep.append(dolar)
    lista_ticker = []
    lista_ticker.append(simbolo+'D')
    lista_ticker.append(dolar)
    lista_datos.append(lista_ticker)
# mep_promedio = (sum(lista_mep)/len(lista_mep))      # obtengo el MEP promedio
# print('MEP promedio: ' + str(round(mep_promedio,2)))
planilla = pandas.DataFrame(lista_datos, columns=["TICKER","MEP"])
print(planilla)
