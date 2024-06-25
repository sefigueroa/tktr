import pandas as pd
from pyfiglet import Figlet
from os import remove, rename
from os import path
from datetime import datetime
from dateutil.relativedelta import relativedelta


#Directorio de entrada:
inputDir = "./tkt_masivo_correctivos_filesystem/input/"

#Directorio de salida:
outputDir = "./tkt_masivo_correctivos_filesystem/output/"

#Directorio de constantes:
consDir = "./tkt_masivo_correctivos_filesystem/constantes/"

#Input constantes Coordinadores Torres y Regiones
consCoordinadores = "coordinadoresTorresRegiones.xlsx"

#Input Configuraciones (por ej periodo):
inputConfigFile = "./tkt_masivo_correctivos_filesystem/config.ini"

#Input correctivos
inputCorrectivosFile = "correctivos.xlsx"

#Input previamente generados (export de Service Now):
inputSucceeded = "sc_req_item.xlsx"

#Output archivo para tickets masivos
outputFileTktsMasivos = "Tickets.xlsx"

#URLs Teams
#Con estas partes estaticas concateno variables para construir las URLs de los checklists en teams
##Base estatica:
urlBaseGenerados = "https://ypf.sharepoint.com/:f:/r/sites/msteams_82a1b4/Documentos%20compartidos/Checklist%20Generados%20Mensuales"
urlTailGenerados = "?csf=1&web=1"

urlBaseRealizados = "https://ypf.sharepoint.com/:f:/r/sites/msteams_82a1b4/Documentos%20compartidos/Checklist%20Realizados"
urlTailRealizados = "?csf=1&web=1"

#Dataframe que relaciona el Mes en texto con el Mes en numeros
#Se puede hacer con la funcion datetime, calendar, etc... pero hay que tocar tambien el Locale para que salga en español y depende del OS
dfMeses = pd.DataFrame()
dfMeses['textoMes'] = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
dfMeses['numeroMes'] = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"]

#---------------------------------------------------------------------------------------#

#Contexto de ejecucion: perdiodo para el que se estan creando los tickets
#contextYear = '2023'
#contextMonth = '03'
#configuracion por archivo (chatGPT)
import configparser

# Crea un objeto ConfigParser
config = configparser.ConfigParser()

try:
    # Lee los valores de configuración del archivo
    config.read(inputConfigFile)
    # Obtiene los valores de configuración
    contextYear = config.get('CONFIG', 'contextYear')
    contextMonth = config.get('CONFIG', 'contextMonth')

    #valido que el año no sea mayor a 2024 ni anterior a 2023:
    if 2023 <= int(contextYear) < 2025:
        # Verifica si contextMonth está dentro del rango deseado
        if 1 <= int(contextMonth) <= 12:
            True
        else:
            raise ValueError("El valor de contextMonth no está dentro del rango deseado")
            print("contextMonth:", contextMonth)
            exit()
    else:
        raise ValueError("El valor de contextYear no está dentro del rango deseado")
        print("contextYear:", contextYear)
        exit()
except Exception as e:
    print("Error en el archivo de configuración: ", e)
    exit()

contextPeriod = contextMonth+"/"+contextYear

#Banner
f = Figlet(font='small')
banner = f.renderText('TKTs Masivos - CORRECTIVOS')
print(banner)

#Formato objetivo:
#Titulo,Descripcion,Solicitado_Para,CI,Grupo_Resolutor
#PDMC-cardinalidad-nroVisita-Region-año-mes,nroVisita-URLcarpeta,idCoordinador,ci,grupo

#Cargo el Dataframe de input de correctivos:
try:
    dfModel = pd.read_excel(inputDir + inputCorrectivosFile)
except FileNotFoundError:
    print("Error al leer el archivo ", inputDir+inputCorrectivosFile)
    exit()


#----------Serie "Solicitado_Para" (esto va primero asi el nombre del coordinador está disponible para la Descripcion)

#leo los coordinadores
try:
    dfCoordinadores = pd.read_excel(consDir + consCoordinadores)
except FileNotFoundError:
    print("Error al leer el archivo ", consDir + consCoordinadores)
    exit()

#Agrego el coordinador segun la Torre y la Region (inner join por dos claves)

dfModel = pd.merge(dfModel,dfCoordinadores,on=['TORRE','REGION'], how="inner")

#----------Serie (Columna) "Titulo"
#Extraigo el año y el mes de la columna "Programacion":
# Puedes convertir la columna a tipo datetime
dfModel['PROGRAMACION'] = pd.to_datetime(dfModel['PROGRAMACION'], format='%d/%m/%Y')


#Mes como texto ("Enero" en lugar de "01")
#dfModel['tmTitulo'] = pd.Series("PDM-" + dfModel['N° Visita Link'].astype(str) + "-" + dfModel['FKSitio'].str.partition("-")[2].str.partition("-")[0].astype(str) + "-" + dfModel['Torre'].astype(str) + "-" + dfModel['auxAño'] + "-" + dfModel['textoMes'])
#Mes como numero ("01" en lugar de "Enero")
dfModel['tmTitulo'] = pd.Series("PDMC-" + dfModel['VISITA'].astype(str) + "-" + dfModel['REGION'] + "-" + dfModel['PROGRAMACION'].dt.strftime('%Y') + "-" + dfModel['PROGRAMACION'].dt.strftime('%m'))

#Añado cardinalidad:

# Utiliza el método groupby y cumcount para enumerar los registros repetidos dentro de cada grupo
dfModel['tmTitulo'] += dfModel.groupby('tmTitulo').cumcount().add(1).astype(str).radd('-')

#Pego la cardinalidad en titulo nuevo pero le añado #

#trato a tmTitulo como string
dfModel['tmTitulo'] = dfModel['tmTitulo'].astype(str)

# Le cambiamos de lugar la cardinalidad
dfModel['tmTitulo'] = dfModel['tmTitulo'].str.split('-')
dfModel['tmTitulo'] = dfModel['tmTitulo'].str[0] + '-' + dfModel['tmTitulo'].str[1] + '-' + dfModel['tmTitulo'].str[-1] + '-' + dfModel['tmTitulo'].str[2] + '-' + dfModel['tmTitulo'].str[3] + '-' + dfModel['tmTitulo'].str[4]

#----------Serie "Descripcion":

#Para la descripcion, armo una columna auxiliar con el año y el mes de programacion (le saco el dia)

#2023-01-14
#Antes se usaba "Fecha Programación", cuando el periodo pasó a medirse de 21 a 20 comenzamos a utilizar la columna "Programación" en su lugar
#dfModel["auxAño"] = (dfModel["Programacion"].astype(str).str.split("-", n=2, expand=True))[0]

dfModel["auxMes"] = dfModel['PROGRAMACION'].dt.strftime('%m')

#Reemplazo el mes innerjoineando con el dataframe de constantes de meses y numeros

dfModel = pd.merge(dfModel, dfMeses,left_on='auxMes', right_on='numeroMes', how="inner")

#armo la columna con las URLs de checklists generados:
dfModel["auxUrlGenerados"] = pd.Series(urlBaseGenerados + "/" + dfModel["REGION"] + "/" + dfModel['PROGRAMACION'].dt.strftime('%Y') + "/" + dfModel['PROGRAMACION'].dt.strftime('%m') + "%20-%20" + dfModel["textoMes"] + "/" + dfModel["TORRE"] + urlTailGenerados)

#armo la columna con las URLs de checklists realizados:
dfModel["auxUrlRealizados"] = pd.Series(urlBaseRealizados + "/" + dfModel["REGION"] + "/" + dfModel['PROGRAMACION'].dt.strftime('%Y') + "/" + dfModel['PROGRAMACION'].dt.strftime('%m') + "%20-%20" + dfModel["textoMes"] + "/" + dfModel["TORRE"] + urlTailRealizados)

#formateo columnas estandarizadas e indico valores si vacío:
dfModel["PRIORIDAD"] = dfModel["PRIORIDAD"].str.upper()
dfModel['PRIORIDAD'] = dfModel['PRIORIDAD'].fillna('<No especificado>')

dfModel["CI"] = dfModel["CI"].str.upper()
dfModel['CI'] = dfModel['CI'].fillna('<No especificado>')

dfModel["DESCRIPCION"] = dfModel["DESCRIPCION"].str.upper()
dfModel['DESCRIPCION'] = dfModel['DESCRIPCION'].fillna('<No especificado>')

dfModel["OBSERVACIONES"] = dfModel["OBSERVACIONES"].str.upper()
dfModel['OBSERVACIONES'] = dfModel['OBSERVACIONES'].fillna('<No especificado>')

dfModel["REALIZADO POR"] = dfModel["REALIZADO POR"].str.upper()
dfModel['REALIZADO POR'] = dfModel['REALIZADO POR'].fillna('<No especificado>')


#Armo la descripcion:
dfModel['tmDescripcion'] = pd.Series("Mantenimiento preventivo surgido de la visita ".upper() + dfModel['VISITA'].astype(str) + " realizada por ".upper() + dfModel['TORRE'] + " " + dfModel['REGION'] + "\n" 
                                     + "PRIORIDAD: " + dfModel['PRIORIDAD'].astype(str) + "\n\n" 
                                     + "DETALLE:" + "\n" 
                                     + dfModel['DESCRIPCION'].astype(str) + "\n\n" 
                                     + "CI:" + dfModel['CI'].astype(str) + "\n\n" 
                                     + "OBSERVACIONES:" + "\n" 
                                     + dfModel['OBSERVACIONES'].astype(str) + "\n\n" 
                                     + "TÉCNICO QUE REALIZÓ EL MANTENIMIENTO PREVENTIVO: " + dfModel['REALIZADO POR'].astype(str) + "\n\n" 
                                     + "GRUPO RESOLUTOR DEL PDM: " + dfModel['GRUPO PDM'].astype(str) + "\n\n" 
                                     + "DE SER NECESARIO, DEBERÁ TRANSFERIRSE ESTE TICKET AL GRUPO RESOLUTOR RESPONSABLE DE REALIZAR EL MANTENIMIENTO CORRECTIVO." + "\n\n" 
                                     + "SOLICITADO PARA: " + dfModel["FULLNAMECOORDINADOR"] + "\n\n"
                                     + "CHECKLISTS GENERADOS :" + "\n"
                                     + dfModel["auxUrlGenerados"]  + "\n"
                                     + "INFORMES REALIZADOS :" + "\n"
                                     + dfModel["auxUrlRealizados"]
                                     )


#reduzco el df a las columnas que necesito (el resto de columnas las descarto)
dfModel = pd.DataFrame(dfModel[['tmTitulo','tmDescripcion','IDCOORDINADOR','GRUPO CORRECTIVO']])

#renombro las columnas para que coincida con el formato destino
dfModel = dfModel.rename(columns={'tmTitulo':'Titulo','tmDescripcion':'Descripcion','IDCOORDINADOR':'Solicitado_Para', 'GRUPO CORRECTIVO':'Grupo_Resolutor'})

#inserto la columna CI
dfModel.insert(3,"CI","")#va sin datos por default

#VALIDACION DE PREXISTENTES

#una vez genereado el nuevo archivo, lo comparo con el generado desde Service Now (es input)
##la idea es no generar dos veces el mismo tkt

print("Quitando correctivos previamente ticketizados")

#Abro el export de Service Now
try:
    dfSucceeded = pd.read_excel(inputDir + inputSucceeded)
except FileNotFoundError:
    print("Error al leer el archivo ", inputDir + inputSucceeded)
    exit()
#dejo solamente la descripcion que es lo que necesito realmente:
serieSucceeded = dfSucceeded['Descripción']

dfToReduce = dfModel

toRemoveList = serieSucceeded.values.tolist()

#reducir con service now
dfToReduce = dfToReduce.set_index('Titulo')
bad_index = dfToReduce.index.isin(toRemoveList)
dfReduced = dfToReduce[~bad_index].reset_index()

dfModel = dfReduced

#Si el dataframe quedo vacio, no guardo datos y detengo ejecucion
if dfModel.empty:
    print("***Revisar configuracion y contexto: Al finalizar, no hay datos para generar tickets")
    exit()

#Guardo los datos en el output
try:
    dfModel.to_excel(outputDir + outputFileTktsMasivos, index=False)
except Exception as e:
    print("Error al guardar los datos en el archivo:", str(e))
    exit()

    
#Renombro los archivos procesados para evitar errores(chatGPT)
try:
    # Separa la ruta del archivo de la extensión
    filename, extension = path.splitext(inputCorrectivosFile)

    # Renombra el archivo agregando un guion bajo al final
    new_filename = "_" + filename + extension
    rename(path.join(inputDir, inputCorrectivosFile), path.join(inputDir, new_filename))
    

except Exception as e:
    print(f"Error renombrando el archivo de entrada {inputCorrectivosFile}: {e}")
    exit()

try:
    # Separa la ruta del archivo de la extensión
    filename, extension = path.splitext(inputSucceeded)

    # Renombra el archivo agregando un guion bajo al final
    new_filename = "_" + filename + extension
    rename(path.join(inputDir, inputSucceeded), path.join(inputDir, new_filename))
    

except Exception as e:
    print(f"Error renombrando el archivo de entrada {inputSucceeded}: {e}")
    exit()



print("\nCOMPLETADO\nFIN DEL PROGRAMA PRINCIPAL")
exit()