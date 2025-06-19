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

## SOLUCIÓN DE PROBLEMAS COMUNES

### Bucles de Redirección HTTPS
Si experimentas bucles de redirección, verifica:

1. **Configuración de Django (settings.py)**:
   ```python
   SECURE_SSL_REDIRECT = False  # Azure maneja esto automáticamente
   USE_X_FORWARDED_HOST = True
   SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
   ```

2. **Variables de entorno en Azure**:
   - Ve a: App Service > Configuración > Variables de aplicación
   - Añade: `HTTP_X_FORWARDED_PROTO = https`
   - Añade: `AZURE_HTTPS_HANDLED = true`

3. **Verificar web.config**:
   - No debe incluir reglas de redirección HTTPS
   - Azure maneja HTTPS automáticamente

### Debug en Azure
Para debuggear problemas:

1. **Ejecutar script de debug**:
   ```bash
   # En la consola de Azure (Herramientas de desarrollo > Consola)
   python azure_debug.py
   ```

2. **Revisar logs**:
   ```bash
   # Ver logs de Python
   cat LogFiles/python.log
   
   # Ver logs de Django
   cat django_errors.log
   ```

3. **Verificar variables de entorno**:
   ```bash
   # En la consola de Azure
   env | grep -E "(HTTP_|WEBSITE_|DJANGO_)"
   ```

### Configuración de Cookies Seguras
Para producción, las cookies deben ser seguras:

```python
# En settings.py
SESSION_COOKIE_SECURE = IS_PRODUCTION
CSRF_COOKIE_SECURE = IS_PRODUCTION
```

Si hay problemas, temporalmente desactiva:
```python
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
```
