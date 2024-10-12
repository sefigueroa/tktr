from tktr_app import tkt_masivo_correctivos, tkt_masivo_pdm, misc
import dotenv
import os
from time import sleep

def main():
    # Cargar las variables de entorno desde el archivo .env
    dotenv.load_dotenv()

    # Crear el diccionario con las variables de entorno
    configDic = {
        # General
        'loopSleepTimeSecs': int(os.getenv("LOOPSLEEPTIMESECS", 30)),  # Convertir a int con valor por defecto 30 si no se encuentra

        # URLs Teams
        'urlBaseGenerados': os.getenv("URLBASEGENERADOS"),
        'urlTailGenerados': os.getenv("URLTAILGENERADOS"),
        'urlBaseRealizados': os.getenv("URLBASEREALIZADOS"),
        'urlTailRealizados': os.getenv("URLTAILREALIZADOS"),

        'filesystemPath': os.getenv("FILESYSTEMPATH"),

        # Correctivos
        'pdmc_scrapDir': os.getenv("PDMC_SCRAPDIR"),
        'pdmc_inputDir': os.getenv("PDMC_INPUTDIR"),
        'pdmc_outputDir': os.getenv("PDMC_OUTPUTDIR"),
        'pdmc_inputConfigFile': os.getenv("PDMC_CONFIGFILE"),
        'pdmc_consCoordinadores': os.getenv("PDMC_CONSFILE"),
        'pdmc_inputCorrectivosFile': os.getenv("PDMC_INPUTCORRECTIVOSFILE", "correctivos.xlsx"),  # Asignar nombre por defecto si no se encuentra
        'pdmc_inputSucceededFile':  os.getenv("PDMC_INPUTSUCCEEDEDFILE"),
        'pdmc_outputFileTktsMasivos': os.getenv("PDMC_OUTPUTTKTSFILE"),
        'pdmc_correctivos_file_path': os.path.join(os.getenv("FILESYSTEMPATH"), os.getenv("PDMC_INPUTDIR"), os.getenv("PDMC_INPUTCORRECTIVOSFILE")),
        'pdmc_correctivos_constantes_file_path': os.path.join(os.getenv("FILESYSTEMPATH"), os.getenv("PDMC_CONSDIR"), os.getenv("PDMC_CONSFILE")),
        'pdmc_inputSucceededFilePath': os.path.join(os.getenv("FILESYSTEMPATH"), os.getenv("PDMC_INPUTDIR"), os.getenv("PDMC_INPUTSUCCEEDEDFILE")),
        'pdmc_outputDirPath': os.path.join(os.getenv("FILESYSTEMPATH"), os.getenv("PDMC_OUTPUTDIR")),
        'pdmc_scrapDirPath': os.path.join(os.getenv("FILESYSTEMPATH"), os.getenv("PDMC_SCRAPDIR")),
        
        # Preventivos (PDM)
        'pdm_scrapDir': os.getenv("PDM_SCRAPDIR"),
        'pdm_inputDir': os.getenv("PDM_INPUTDIR"),
        'pdm_outputDir': os.getenv("PDM_OUTPUTDIR"),
        'pdm_inputConfigFile': os.getenv("PDM_CONFIGFILE"),
        'pdm_consCoordinadores': os.getenv("PDM_CONSFILE"),
        'pdm_inputPdmFile': os.getenv("PDM_INPUTPLANFILE", "data.xlsx"),  # Asignar nombre por defecto si no se encuentra el archivo indicado
        'pdm_inputSucceededFile':  os.getenv("PDM_INPUTSUCCEEDEDFILE"), # Archivo con los tkts preexistentes. Se utiliza para eliminar los previmanete creados y no duplicar tkts
        'pdm_outputFileTktsMasivos': os.getenv("PDM_OUTPUTTKTSFILE"),
        'pdm_pdm_file_path': os.path.join(os.getenv("FILESYSTEMPATH"), os.getenv("PDM_INPUTDIR"), os.getenv("PDM_INPUTPLANFILE")),
        'pdm_pdm_constantes_file_path': os.path.join(os.getenv("FILESYSTEMPATH"), os.getenv("PDM_CONSDIR"), os.getenv("PDM_CONSFILE")),
        'pdm_pdm_grupos_file_path': os.path.join(os.getenv("FILESYSTEMPATH"), os.getenv("PDM_CONSDIR"), os.getenv("PDM_GROUPSCONSFILE")),
        'pdm_inputSucceededFilePath': os.path.join(os.getenv("FILESYSTEMPATH"), os.getenv("PDM_INPUTDIR"), os.getenv("PDM_INPUTSUCCEEDEDFILE")),
        'pdm_outputDirPath': os.path.join(os.getenv("FILESYSTEMPATH"), os.getenv("PDM_OUTPUTDIR")),
        'pdm_scrapDirPath': os.path.join(os.getenv("FILESYSTEMPATH"), os.getenv("PDM_SCRAPDIR"))
        
    }

    while True:
        print("-" * 50)
        # Verificar si los archivos existen antes de continuar
        if not os.path.exists(configDic['pdmc_correctivos_file_path']):
            print("Sin CORRECTIVOS para procesar...")
        elif os.path.exists(configDic['pdmc_correctivos_file_path']):
            print("----PROCESANDO CORRECTIVOS----")
            # Limpiar el output:
            # Borra todo el contenido de outputs
            misc.limpiarDirectorio(configDic['pdmc_outputDirPath'])
            # Procesar Correctivos:
            tkt_masivo_correctivos.proc_correctivos(configDic)
            #Mover al scrap lo procesado:
            inputsList = [configDic['pdmc_correctivos_file_path'], configDic['pdmc_inputSucceededFilePath']]
            misc.move2scrap(configDic['pdmc_scrapDirPath'], inputsList)
            print("-"*40)
        if not os.path.exists(configDic['pdm_pdm_file_path']):
            print("Sin Planificacion PDM para procesar...")
        elif os.path.exists(configDic['pdm_pdm_file_path']):
            print("----PROCESANDO PLANIFICACION DE PDM----")
            # Limpiar el output:
            # Borra todo el contenido de outputs
            misc.limpiarDirectorio(configDic['pdm_outputDirPath'])
            # Procesar PDM:
            tkt_masivo_pdm.proc_tktsPdm(configDic)
            #Mover al scrap lo procesado:
            inputsList = [configDic['pdm_pdm_file_path'], configDic['pdm_inputSucceededFilePath']]
            misc.move2scrap(configDic['pdm_scrapDirPath'], inputsList)
            print("-"*40)
        # Espera entre ciclos
        sleep(configDic['loopSleepTimeSecs'])

if __name__ == "__main__":
    main()
