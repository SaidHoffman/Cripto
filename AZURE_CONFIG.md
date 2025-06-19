# Configuración específica para Azure App Service
# Este archivo contiene variables de entorno y configuraciones
# que deben ser establecidas en Azure para evitar bucles de redirección

# Variables de entorno que deben configurarse en Azure App Service
# Ir a: Configuración > Variables de aplicación

# 1. Variables básicas de Django
DJANGO_SETTINGS_MODULE=dental_project.settings
PYTHONPATH=/home/site/wwwroot

# 2. Variables específicas para evitar bucles HTTPS
# Estas le dicen a Django que Azure ya maneja HTTPS
AZURE_HTTPS_HANDLED=true
HTTP_X_FORWARDED_PROTO=https

# 3. Variables de base de datos (si usas Azure SQL en el futuro)
# DATABASE_URL=postgresql://usuario:password@servidor.postgres.database.azure.com:5432/basedatos

# 4. Variables de seguridad para producción
DJANGO_SECRET_KEY=tu_clave_secreta_aqui
DJANGO_DEBUG=False

# 5. Configuraciones de logging
DJANGO_LOG_LEVEL=ERROR

# INSTRUCCIONES PARA CONFIGURAR EN AZURE:
# 1. Ve a tu App Service en el Portal de Azure
# 2. Navega a Configuración > Variables de aplicación
# 3. Añade cada variable como "Configuración de la aplicación"
# 4. Reinicia la aplicación después de hacer cambios

# COMANDOS ÚTILES PARA DEBUGGING EN AZURE:
# Para acceder a la consola de Azure:
# 1. Ve a Herramientas de desarrollo > Consola
# 2. Ejecuta: python azure_debug.py
# 3. Revisa los logs en: LogFiles/python.log

# VERIFICACIONES POST-DESPLIEGUE:
# 1. Verificar que no hay bucles de redirección HTTP -> HTTPS
# 2. Verificar que las cookies se configuran correctamente
# 3. Verificar que las URLs de login/logout funcionan
# 4. Verificar que los archivos estáticos se sirven correctamente
