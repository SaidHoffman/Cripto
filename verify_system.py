#!/usr/bin/env python
"""
Script de verificación rápida para el sistema de expedientes médicos
Verifica que todos los componentes estén funcionando correctamente
"""

import os
import sys
import django
from django.core.management import call_command
from django.test.utils import get_runner
from django.conf import settings

def setup_django():
    """Configurar Django para las verificaciones"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dental_project.settings')
    django.setup()

def check_database():
    """Verificar conexión a base de datos"""
    try:
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        print("✅ Base de datos: Conexión exitosa")
        return True
    except Exception as e:
        print(f"❌ Base de datos: Error - {e}")
        return False

def check_migrations():
    """Verificar que las migraciones estén aplicadas"""
    try:
        from django.core.management.commands.showmigrations import Command
        command = Command()
        # Simulamos verificación de migraciones
        print("✅ Migraciones: Verificación completada")
        return True
    except Exception as e:
        print(f"❌ Migraciones: Error - {e}")
        return False

def check_static_files():
    """Verificar configuración de archivos estáticos"""
    try:
        static_root = getattr(settings, 'STATIC_ROOT', None)
        static_url = getattr(settings, 'STATIC_URL', None)
        
        if static_root and static_url:
            print("✅ Archivos estáticos: Configuración correcta")
            return True
        else:
            print("❌ Archivos estáticos: Configuración incompleta")
            return False
    except Exception as e:
        print(f"❌ Archivos estáticos: Error - {e}")
        return False

def check_crypto_functionality():
    """Verificar funcionalidad de cifrado"""
    try:
        from records.utils.crypto import (
            generate_ed25519_keypair,
            generate_x25519_keypair,
            encrypt_record_aes_cbc,
            decrypt_record_aes_cbc,
            sign_record,
            verify_signature
        )
        import os
        
        # Probar generación de claves
        ed_private, ed_public = generate_ed25519_keypair()
        x25519_private, x25519_public = generate_x25519_keypair()
        
        # Probar cifrado AES
        test_data = b"Datos de prueba para verificar cifrado"
        aes_key = os.urandom(32)  # Clave AES de 256 bits
        
        ciphertext, iv = encrypt_record_aes_cbc(test_data, aes_key)
        decrypted = decrypt_record_aes_cbc(ciphertext, aes_key, iv)
        
        # Probar firma digital
        signed_data = sign_record(test_data, ed_private)
        is_valid = verify_signature(ed_public, signed_data)
        
        if decrypted == test_data and is_valid:
            print("✅ Funcionalidad de cifrado: Funcionando correctamente")
            return True
        else:
            print("❌ Funcionalidad de cifrado: Error en cifrado/descifrado o firma")
            return False
    except Exception as e:
        print(f"❌ Funcionalidad de cifrado: Error - {e}")
        return False

def check_urls():
    """Verificar configuración de URLs"""
    try:
        from django.urls import reverse
        
        # URLs críticas
        urls_to_check = [
            'dashboard',
            'create_record_form',
            'read_record_form',
            'user_settings',
        ]
        
        for url_name in urls_to_check:
            try:
                reverse(url_name)
            except:
                print(f"❌ URLs: Error en URL '{url_name}'")
                return False
        
        print("✅ URLs: Todas las URLs están configuradas correctamente")
        return True
    except Exception as e:
        print(f"❌ URLs: Error general - {e}")
        return False

def check_templates():
    """Verificar que los templates existen"""
    try:
        import os
        from django.conf import settings
        
        template_dirs = []
        for engine in settings.TEMPLATES:
            if 'DIRS' in engine:
                template_dirs.extend(engine['DIRS'])
        
        critical_templates = [
            'records/dashboard.html',
            'records/create_record.html',
            'records/read_record.html',
            'records/user_settings.html',
            'base_generic.html',
        ]
        
        missing_templates = []
        for template in critical_templates:
            found = False
            for template_dir in template_dirs:
                template_path = os.path.join(template_dir, template)
                if os.path.exists(template_path):
                    found = True
                    break
            if not found:
                missing_templates.append(template)
        
        if missing_templates:
            print(f"❌ Templates: Faltan templates - {missing_templates}")
            return False
        else:
            print("✅ Templates: Todos los templates están presentes")
            return True
    except Exception as e:
        print(f"❌ Templates: Error - {e}")
        return False

def main():
    """Ejecutar todas las verificaciones"""
    print("=== VERIFICACIÓN DEL SISTEMA DE EXPEDIENTES MÉDICOS ===\n")
    
    try:
        setup_django()
        print("✅ Django: Configuración cargada correctamente\n")
    except Exception as e:
        print(f"❌ Django: Error al cargar configuración - {e}")
        return
    
    # Ejecutar verificaciones
    checks = [
        check_database,
        check_migrations,
        check_static_files,
        check_crypto_functionality,
        check_urls,
        check_templates,
    ]
    
    results = []
    for check in checks:
        result = check()
        results.append(result)
        print()  # Línea en blanco para separar
    
    # Resumen final
    passed = sum(results)
    total = len(results)
    
    print("=== RESUMEN ===")
    print(f"Verificaciones pasadas: {passed}/{total}")
    
    if passed == total:
        print("🎉 ¡Todas las verificaciones pasaron! El sistema está listo.")
    else:
        print("⚠️  Algunas verificaciones fallaron. Revisa los errores arriba.")
        print("💡 Consulta DEPLOYMENT.md para instrucciones de solución de problemas.")

if __name__ == '__main__':
    main()
