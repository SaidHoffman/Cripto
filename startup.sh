#!/bin/bash

# Script de inicialización para Azure App Service
echo "Iniciando configuración de producción..."

# Instalar dependencias
pip install -r requirements.txt

# Recopilar archivos estáticos
python manage.py collectstatic --noinput

# Ejecutar migraciones
python manage.py migrate

echo "Configuración completada!"
