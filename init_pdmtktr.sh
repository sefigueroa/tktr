#!/bin/bash

# Inicializacion de Correctivos:
if [ ! -f /app/filesystem/pdmtktr/correctivos/config.ini ]; then
  echo "Copiando archivo de configuración predeterminado para correctivos..."
  cp /app/templates/correctivos/config.ini /app/filesystem/pdmtktr/correctivos/config.ini
fi

if [ ! -f /app/filesystem/pdmtktr/correctivos/constantes/coordinadoresTorresRegiones.xlsx ]; then
  echo "Copiando archivo coordinadoresTorresRegiones.xlsx para correctivos (Constantes)..."
  mkdir -p /app/filesystem/pdmtktr/correctivos/constantes
  cp /app/templates/correctivos/constantes/coordinadoresTorresRegiones.xlsx /app/filesystem/pdmtktr/correctivos/constantes/coordinadoresTorresRegiones.xlsx
fi

#Inicializacion de Planificacion PDM
if [ ! -f /app/filesystem/pdmtktr/pdm/config.ini ]; then
  echo "Copiando archivo de configuración predeterminado para planificacion pdm..."
  cp /app/templates/pdm/config.ini /app/filesystem/pdmtktr/pdm/config.ini
fi

if [ ! -f /app/filesystem/pdmtktr/pdm/constantes/coordinadoresTorresRegiones.xlsx ]; then
  echo "Copiando archivo coordinadoresTorresRegiones.xlsx para planificacion pdm (Constantes)..."
  mkdir -p /app/filesystem/pdmtktr/pdm/constantes
  cp /app/templates/pdm/constantes/coordinadoresTorresRegiones.xlsx /app/filesystem/pdmtktr/pdm/constantes/coordinadoresTorresRegiones.xlsx
fi

if [ ! -f /app/filesystem/pdmtktr/pdm/constantes/gruposPDM.xlsx ]; then
  echo "Copiando archivo gruposPDM.xlsx para planificacion pdm (Constantes)..."
  mkdir -p /app/filesystem/pdmtktr/pdm/constantes
  cp /app/templates/pdm/constantes/gruposPDM.xlsx /app/filesystem/pdmtktr/pdm/constantes/gruposPDM.xlsx
fi