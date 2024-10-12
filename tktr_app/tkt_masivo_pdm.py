import openpyxl.styles
import pandas as pd
from pyfiglet import Figlet
from os import remove, rename
from os import path
from datetime import datetime
from dateutil.relativedelta import relativedelta
import openpyxl
import os
import warnings

# Silencia el UserWarning específico de openpyxl
warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")


"""
#Directorio de entrada:
inputDir = "./tkt_masivo_pdm_filesystem/input/"

#Directorio de salida:
outputDir = "./tkt_masivo_pdm_filesystem/output/"

#Directorio de constantes:
consDir = "./tkt_masivo_pdm_filesystem/constantes/"

#Input constantes Grupos y Cuadrillas
consGruposCuadrillas = "gruposPDM.xlsx"

#Input constantes Coordinadores Torres y Regiones
consCoordinadores = "coordinadoresTorresRegiones.xlsx"

#Input Configuraciones (por ej periodo):
inputConfigFile = "./tkt_masivo_pdm_filesystem/config.ini"

#Input datos powerBI (data input)
inputDataFile = "data.xlsx"

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
"""
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

def proc_tktsPdm(configDic):

    #Variables de configuracion:
    # Filesystem:
    fileSystemDir = configDic['filesystemPath']

    # Obtiene las variables de configuracion:
    inputDir = configDic['pdm_inputDir']
    outputDir = configDic['pdm_outputDir']

    # Input constantes Coordinadores Torres y Regiones:
    consCoordinadores = configDic['pdm_consCoordinadores']

    # Inputconstates Coordinadores... filepath directo:
    constantes_file_path = configDic['pdm_pdm_constantes_file_path']

    #Input de grupos de PDM:
    constantes_gruposPDM_file_path = configDic['pdm_pdm_grupos_file_path']

    # Input Configuraciones (por ej periodo):
    inputConfigFile = path.join(configDic['filesystemPath'], configDic['pdm_inputConfigFile'])
    
    # Input planificacion pdm:
    inputPdmFile = configDic['pdm_inputPdmFile']

    # Input planificacion pdm ruta (path completo):
    inputPdmFilePath = configDic['pdm_pdm_file_path']

    # Input tkts PDM previamente generados (export de Service Now):
    inputSucceededFile = configDic['pdm_inputSucceededFile']

    # input previamente generados PATH DIRECTO:
    pdm_inputSucceededFilePath = configDic['pdm_inputSucceededFilePath']

    # Output archivo para tickets masivos:
    outputFileTktsMasivos = configDic['pdm_outputFileTktsMasivos']

    # URLs Teams:
    urlBaseGenerados = configDic['urlBaseGenerados']
    urlTailGenerados = configDic['urlTailGenerados']

    urlBaseRealizados = configDic['urlBaseRealizados']
    urlTailRealizados = configDic['urlTailRealizados']

    # Crea un objeto ConfigParser
    config = configparser.ConfigParser()

    try:
        # Lee los valores de configuración del archivo
        config.read(inputConfigFile)
        # Obtiene los valores de configuración
        contextYear = config.get('CONFIG', 'contextYear')
        contextMonth = config.get('CONFIG', 'contextMonth')
        contextVersion = config.get('CONFIG', 'contextVersion')

        #valido que el año no sea mayor a 2024 ni anterior a 2023: (por que no lo dejaba ser mas alla del 2025???)
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
    banner = f.renderText('TKTs Masivos - PDM')
    print(banner)

    #Formato objetivo:
    #Titulo,Descripcion,Solicitado_Para,CI,Grupo_Resolutor
    #PDM-nroVisita-Region-Torre,nroVisita-URLcarpeta,idCoordinador,ci,grupo

    #cahtgpt validando la lectura del archivo
    try:
        dfModel = pd.read_excel(inputPdmFilePath)
    except FileNotFoundError:
        print("Error al leer el archivo ", inputPdmFilePath)
        exit()

    #recorto el footer que trae el export:
    footer = 3 #(esto es para elimina el pie de pagina que mete PowerBi)
    filas = (dfModel.size / 12) - footer
    dfModel = dfModel.drop(dfModel.index[int(filas):int(dfModel.size/12)])

    #quito los que no sean del periodo preconfigurado en contextPeriod:

    contextPeriodDTMin = datetime.strptime(contextPeriod, '%m/%Y')
    contextPeriodDTMax = contextPeriodDTMin + relativedelta(months=1)

    #mayor al primer dia del periodo de contexto (antes usaba "Fecha Programación", luego cuando pasó de 21 a 20 el periodo se comenzó a utlizar "Programación" en su lugar)
    dfModel = dfModel[ (dfModel["Programacion"] >= contextPeriodDTMin)]
    #menor al siguiente periodo, es decir, hasta el ultimo dia del periodo de contexto
    dfModel = dfModel[ (dfModel["Programacion"] < contextPeriodDTMax)]

    #Detengo ejecucion si me queda vacio el dfModel luego de limpiarlo
    if dfModel.empty:
        print("***Revisar periodo/datos powerBI: Al aplicar filtro de periodo el dataframe quedo vacio")
        exit()

    #Reviso que minimamente la informacion de las Torres y Regiones sea coherente:

    dfModelCheck = dfModel.copy()

    dfModelCheck['REGION'] = dfModelCheck['FKSitio'].astype(str).apply(lambda x: '-'.join(x.split('-')[1:2]))

    region_values = ['CENTRONORTE', 'CUYO', 'SUR', 'OESTE']
    torre_values = ['SOPORTE', 'COMUNICACIONES', 'INFRAESTRUCTURA']

    match_torre = dfModelCheck[~dfModelCheck['Torre'].isin(torre_values)]
    match_region = dfModelCheck[~dfModelCheck['REGION'].isin(region_values)]

    salir=0 #claramente esto era por hacerlo rapido.. salir=0 ? jajaja
    if match_region.empty:
        print('Regiones OK!')
    else:
        print('WARNING: Se encontro un error en las Regiones!')
        salir=1
    if match_torre.empty:
        print('Torres OK!')
    else:
        print('WARNING: Se encontro un error en las Torres!')
        salir=1

    if salir:
        quit()

    #analizar programacion para evitar DUPLICADOS. Si encuentra Duplicados abortar ejecucion.
    # Detectar duplicados basados en las columnas 'Nombre' y 'Apellido'
    duplicados = dfModel.duplicated(subset=['FKSitio', 'KeyEspecialidad'], keep=False)

    # Filtrar el DataFrame para mostrar sólo los registros duplicados
    df_duplicados = dfModel[duplicados]
    if df_duplicados.empty:
        True
    else:
        # Mostrar los duplicados
        print("-"*40)
        print("ATENCIÓN!!: REGISTROS DUPLICADOS EN PLANIFICACION DE POWERBI: ")
        print("-"*40)
        #print(df_duplicados)
        #guardar los duplicados para su revision:
        df_duplicados.to_excel(fileSystemDir+outputDir+"/"+"DUPLICADOS.xlsx")


    #----------Serie "Descripcion":
    #mapeo de urls lo toma por variables al inicio

    #Agrego una Columna para la region, y Modifico la de la Torre para que tenga solo la primera en mayusculas

    #Formato ejemplo: Sitio-CUYO-2 VM-OFICINA - PLANTA DE GAS
    #atencion al ", n=2, expand=True". Si no le indico asi, split solo da error
    #como siempre el formato va a ser Sitio-Region-algo, ya se que al menos 2 veces el guion aparece
    #de paso el ,title para dejar solo la primera en mayusculas...
    dfModel["auxRegion"] = (dfModel["FKSitio"].str.split("-", n=2, expand=True))[1].str.title()

    dfModel['Torre'] = dfModel['Torre'].str.title()

    #Para la descripcion, armo una columna auxiliar con el año y el mes de programacion (le saco el dia)

    #2023-01-14
    #Antes se usaba "Fecha Programación", cuando el periodo pasó a medirse de 21 a 20 comenzamos a utilizar la columna "Programación" en su lugar
    dfModel["auxAño"] = (dfModel["Programacion"].astype(str).str.split("-", n=2, expand=True))[0]

    dfModel["auxMes"] = dfModel["Programacion"].astype(str).str.split("-", n=2, expand=True)[1]

    #Reemplazo el mes innerjoineando con el dataframe de constantes de meses y numeros

    dfModel = pd.merge(dfModel, dfMeses,left_on='auxMes', right_on='numeroMes', how="inner")

    #armo la columna con las URLs de checklists generados:
    dfModel["auxUrlGenerados"] = pd.Series(urlBaseGenerados + "/" + dfModel["auxRegion"] + "/" + dfModel["auxAño"] + "/" + dfModel["numeroMes"] + "%20-%20" + dfModel["textoMes"] + "/" + dfModel["Torre"] + urlTailGenerados)

    #armo la columna con las URLs de checklists realizados:
    dfModel["auxUrlRealizados"] = pd.Series(urlBaseRealizados + "/" + dfModel["auxRegion"] + "/" + dfModel["auxAño"] + "/" + dfModel["numeroMes"] + "%20-%20" + dfModel["textoMes"] + "/" + dfModel["Torre"] + urlTailRealizados)

    #Armo la descripcion:

    dfModel['tmDescripcion'] = pd.Series("Nro de Visita: " + dfModel['N° Visita Link'].astype(str) + '\n' + "CheckLists Generados:" + '\n' + dfModel['auxUrlGenerados'].astype(str) + '\n' + "Informes Realizados:" +'\n' + dfModel['auxUrlRealizados'].astype(str))

    # Armo el encabezado para el Periodo_PDMP
    dfModel['Periodo_PDMP'] = pd.Series(dfModel['auxAño'] + "-" + dfModel['numeroMes'])

    # Armo el encabezado para la Fecha_Planificada
    dfModel['Fecha_Planificada'] =  '20/' + pd.Series(dfModel["numeroMes"] + '/' + dfModel["auxAño"])

    #----------Serie (Columna) "Titulo" (va en este orden para disponer de auxAño por ej)
    #Mes como texto ("Enero" en lugar de "01")
    #dfModel['tmTitulo'] = pd.Series("PDM-" + dfModel['N° Visita Link'].astype(str) + "-" + dfModel['FKSitio'].str.partition("-")[2].str.partition("-")[0].astype(str) + "-" + dfModel['Torre'].astype(str) + "-" + dfModel['auxAño'] + "-" + dfModel['textoMes'])
    #Mes como numero ("01" en lugar de "Enero")
    dfModel['tmTitulo'] = pd.Series("PDM-" + dfModel['N° Visita Link'].astype(str) + "-" + dfModel['FKSitio'].str.partition("-")[2].str.partition("-")[0].astype(str) + "-" + dfModel['Torre'].astype(str) + "-" + dfModel['auxAño'] + "-" + dfModel['numeroMes'])

    #----------Serie "Solicitado_Para y Grupo_Resolutor"
    #cargo las constantes de Grupo y Cuadrillas para cruzarlo con el df
    try:
        dfConstantes = pd.read_excel(constantes_gruposPDM_file_path)
    except FileNotFoundError:
        print("Error al leer el archivo ", constantes_gruposPDM_file_path)
        exit()
    #hago el innerjoin por Cuadrilla
    dfModel = pd.merge(dfModel, dfConstantes,on='Cuadrilla', how="inner")

    #leo los coordinadores
    try:
        dfCoordinadores = pd.read_excel(constantes_file_path)
    except FileNotFoundError:
        print("Error al leer el archivo ", constantes_file_path)
        exit()

    #Agrego el coordinador segun la Torre y la Region (inner join por dos claves)
    #modifico la columna de region para el inner (podria haber usado solo el upper y cambiar el inner tb)
    dfModel["auxRegion"].str.upper()
    dfModel.rename(columns={'auxRegion':'Region'})

    dfModel["Torre"] = dfModel["Torre"].str.upper()

    dfModel = pd.merge(dfModel,dfCoordinadores,on=['Torre','Region'], how="inner")

    # Este if define que version usar. 1 para la version vieja y 2 para la nueva.
    if contextVersion == '1':
        #reduzco el df a las columnas que necesito (el resto de columnas las descarto)
        dfModel = pd.DataFrame(dfModel[['tmTitulo','tmDescripcion','IdCoordinador','Grupo_Resolutor']])
        #renombro las columnas para que coincida con el formato destino
        dfModel = dfModel.rename(columns={'tmTitulo':'Titulo','tmDescripcion':'Descripcion','IdCoordinador':'Solicitado_Para'})
        #inserto la columna CI
        dfModel.insert(3,"CI","")#va sin datos por default
    elif contextVersion == '2':
        dfModel = pd.DataFrame(dfModel[['tmTitulo',
                                    'IdCoordinador',
                                    'N° Visita Link',
                                    'Periodo_PDMP',
                                    'Region',
                                    'Torre',
                                    'Grupo_Resolutor',
                                    'auxUrlGenerados',
                                    'auxUrlRealizados',
                                    'Fecha_Planificada']])
        
        dfModel = dfModel.rename(columns={'tmTitulo':'Titulo',
                                    'IdCoordinador':'Solicitado_para',
                                    'Grupo_Resolutor':'Grupo_Asignacion',
                                    'N° Visita Link':'Nro_Visita',
                                    'auxUrlGenerados':'Chekclist_generado', # Checklist -> Esta mal escrito porque en SN lo escribieron mal y sino no funciona
                                    'auxUrlRealizados':'Informes_realizados'})
        
        dfModel['Fecha_Planificada'] = pd.to_datetime(dfModel['Fecha_Planificada'], dayfirst=True) # Con esto se le indica a la columna que sea del tipo DATE
        # dfModel['Fecha_Planificada'] = dfModel['Fecha_Planificada'].dt.strftime('%d/%m/%Y')
    else:
        print('El contextVersion debe ser 1(OLD) o 2(NEW). --> Revisar config')
        exit()

    #una vez genereado el nuevo archivo, lo comparo con el generado desde Service Now (es input)
    ##la idea es no generar dos veces el mismo tkt

    print("Quitando sitios/visitas previamente ticketizados")

    #Abro el export de Service Now
    try:
        dfSucceeded = pd.read_excel(pdm_inputSucceededFilePath)
    except FileNotFoundError:
        print("Error al leer el archivo ", pdm_inputSucceededFilePath)
        exit()
    #dejo solamente la descripcion que es lo que necesito realmente:
    serieSucceeded = dfSucceeded['Descripción']

    dfToReduce = dfModel

    toRemoveList = serieSucceeded.values.tolist()

    #reducir con service now
    dfToReduce = dfToReduce.set_index('Titulo')
    bad_index = dfToReduce.index.isin(toRemoveList)
    dfReduced = dfToReduce[~bad_index].reset_index()

    #print("\n\nTickets para generar quitando los previamente generados en Service Now:")
    #print(dfReduced)

    dfModel = dfReduced

    #Si el dataframe quedo vacio, no guardo datos y detengo ejecucion
    if dfModel.empty:
        print("***Revisar configuracion y contexto: Al finalizar, no hay datos para generar tickets")
        exit()

    #Guardo los datos en el output
    try:
        outputTicketsPath = os.path.join(fileSystemDir, outputDir, outputFileTktsMasivos)
        dfModel.to_excel(outputTicketsPath, index=False)
    except Exception as e:
        print("Error al guardar los datos en el archivo:", str(e))
        exit()

    #Reabro el archivo y modifico el formato de la fecha para fecha corta (cosas de Service Now)
    # Cargar el archivo Excel y aplicar el formato de fecha corto
    wb = openpyxl.load_workbook(outputTicketsPath)
    ws = wb.active

    # Crear un estilo de fecha corta
    short_date_style = openpyxl.styles.NamedStyle(name="short_date", number_format="D/M/YYYY")

    # Aplicar el estilo a la columna de fechas
    for cell in ws['J'][1:]:  # Ajusta 'J' a la columna donde están tus fechas
        cell.style = short_date_style

    # Guardar los cambios en el archivo Excel
    wb.save(outputTicketsPath)

    print("\nTKTS PDM: COMPLETADO\n")
