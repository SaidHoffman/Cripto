# Comandos para deployment en Azure

## 1. Preparar archivos estáticos
python manage.py collectstatic --noinput

## 2. Ejecutar migraciones
python manage.py migrate

## 3. Crear superusuario (opcional, solo primera vez)
# python manage.py createsuperuser

## 4. Verificar que todo esté funcionando
python manage.py check --deploy

## 5. Para ejecutar en producción local (testing)
# gunicorn dental_project.wsgi:application

## 6. Para Azure App Service
# El servidor se iniciará automáticamente con el startup.sh
