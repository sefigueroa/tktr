#!/bin/sh
set -x
# Verificar que la variable de entorno ENVIRONMENT esté establecida
#if [ -z "$ENVIRONMENT" ]; then
#  echo "Error: La variable de entorno ENVIRONMENT no está establecida."
#  exit 1
#fi

# Copiar el archivo .env correspondiente
#cp /app/.env.$ENVIRONMENT /app/.env

# Crea la carpeta de input, output y scrap
mkdir -p /app/filesystem/pdmtktr/correctivos/input
mkdir -p /app/filesystem/pdmtktr/correctivos/output
mkdir -p /app/filesystem/pdmtktr/correctivos/scrap

mkdir -p /app/filesystem/pdmtktr/pdm/input
mkdir -p /app/filesystem/pdmtktr/pdm/output
mkdir -p /app/filesystem/pdmtktr/pdm/scrap

#Eliminar basura previa
rm -Rf app/filesystem/pdmtktr/correctivos/output/*
rm -Rf app/filesystem/pdmtktr/pdm/output/*

# Llamar al script de inicialización
./init_pdmtktr.sh

# Ejecutar el comando original
exec "$@"
#exec python run.py
