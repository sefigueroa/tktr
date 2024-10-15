# Usa una imagen base de Python
FROM python:3.12.6-slim

# Establece el directorio de trabajo en /app
WORKDIR /app

# Copia el archivo requirements.txt al directorio de trabajo
COPY requirements.txt .

# Instala las dependencias de la aplicación
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto de la aplicación al directorio de trabajo
COPY . .

# Copia el script de inicio
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
#y copiar el inicializador
COPY init_pdmtktr.sh /init_pdmtktr.sh
RUN chmod +x /init_pdmtktr.sh

# Ejecuta el script de inicio cuando se inicie el contenedor
ENTRYPOINT ["/entrypoint.sh"]
CMD ["python", "-u", "run.py"]