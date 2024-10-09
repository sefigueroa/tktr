#import pandas as pd
#from openpyxl import load_workbook
#from openpyxl.styles import PatternFill, Font
#from openpyxl.worksheet.datavalidation import DataValidation
#import warnings
#from time import sleep
import os
from datetime import datetime
import shutil

import os
import shutil
from datetime import datetime

def move2scrap(scrap_dir, scrapFilePathList):
    print("CORRECTIVOS: Moviendo al Scrap...")
    # Verificar que el directorio scrap exista, de lo contrario crearlo
    if not os.path.exists(scrap_dir):
        os.makedirs(scrap_dir)
    # Obtener el timestamp actual
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    # Iterar sobre cada archivo en la lista
    for file_path in scrapFilePathList:
        if os.path.isfile(file_path):
            # Obtener el nombre del archivo
            file_name = os.path.basename(file_path)

            # Generar un nuevo nombre con el timestamp al inicio
            new_file_name = f"{timestamp}_{file_name}"

            # Crear el nuevo path en el directorio scrap
            new_scrap_path = os.path.join(scrap_dir, new_file_name)

            # Mover el archivo al nuevo path en el directorio scrap
            shutil.move(file_path, new_scrap_path)
            print(f"Archivo movido a scrap: {new_scrap_path}")
        else:
            print(f"El archivo no existe: {file_path}")

    
def limpiarDirectorio(path):
    try:
        # Eliminar todo el contenido del directorio si existe
        if os.path.exists(path):
            shutil.rmtree(path)
        # Recrear el directorio vacío después de borrarlo
        os.makedirs(path)
        print(f"Contenido de {path} eliminado y directorio recreado.")
    except FileNotFoundError:
        print(f"El directorio {path} no existe, no hay nada que borrar.")
    except PermissionError:
        print(f"No se tienen permisos para eliminar el contenido de {path}.")
    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")
