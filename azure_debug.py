#!/usr/bin/env python
"""
Script de debug para Azure App Service
Muestra información útil sobre el entorno de Azure
"""
import os
import sys

def show_azure_env():
    print("=== INFORMACIÓN DEL ENTORNO AZURE ===")
    
    # Variables específicas de Azure
    azure_vars = [
        'WEBSITE_HOSTNAME',
        'WEBSITE_SITE_NAME', 
        'WEBSITE_RESOURCE_GROUP',
        'HTTP_X_FORWARDED_PROTO',
        'HTTP_X_FORWARDED_FOR',
        'HTTP_HOST',
        'SERVER_NAME',
        'SERVER_PORT',
        'HTTPS',
        'REQUEST_SCHEME',
    ]
    
    for var in azure_vars:
        value = os.environ.get(var, 'NO DEFINIDA')
        print(f"{var}: {value}")
    
    print("\n=== CONFIGURACIÓN DJANGO ACTUAL ===")
    
    # Importar settings después de configurar Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dental_project.settings')
    
    try:
        import django
        from django.conf import settings
        django.setup()
        
        print(f"DEBUG: {settings.DEBUG}")
        print(f"ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
        print(f"SECURE_SSL_REDIRECT: {settings.SECURE_SSL_REDIRECT}")
        print(f"SESSION_COOKIE_SECURE: {settings.SESSION_COOKIE_SECURE}")
        print(f"CSRF_COOKIE_SECURE: {settings.CSRF_COOKIE_SECURE}")
        print(f"USE_X_FORWARDED_HOST: {getattr(settings, 'USE_X_FORWARDED_HOST', False)}")
        print(f"SECURE_PROXY_SSL_HEADER: {getattr(settings, 'SECURE_PROXY_SSL_HEADER', None)}")
        print(f"LOGIN_REDIRECT_URL: {settings.LOGIN_REDIRECT_URL}")
        print(f"LOGOUT_REDIRECT_URL: {settings.LOGOUT_REDIRECT_URL}")
        
    except Exception as e:
        print(f"Error al cargar configuración Django: {e}")

if __name__ == '__main__':
    show_azure_env()
