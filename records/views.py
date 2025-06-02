from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt

from .models import EncryptedRecord
from .utils.crypto import encrypt_record_aes_cbc, decrypt_record_aes_cbc

import os


@login_required
def dashboard(request):
    # Obtener los 5 expedientes más recientes (ordenados por timestamp descendente)
    recent_records = EncryptedRecord.objects.order_by('-timestamp')[:5]
    return render(request, 'records/dashboard.html', {
        'recent_records': recent_records
    })


@csrf_exempt
def create_encrypted_record(request):
    """
    Endpoint API (curl/Postman) para cifrar y guardar un expediente mediante JSON o form-data.
    NO SE USA en la interfaz web. Solo acepta POST con:
      - patient_name
      - record
    """
    if request.method == 'POST':
        patient_name = request.POST.get('patient_name', '').strip()
        record_data  = request.POST.get('record', '').encode()

        # Verificar que haya llegado un nombre
        if not patient_name:
            return JsonResponse({'error': 'Missing patient_name'}, status=400)

        key = os.urandom(32)  # AES-256
        ciphertext, iv = encrypt_record_aes_cbc(record_data, key)

        # Guardar o actualizar (si ya existe nombre, lo reemplaza)
        obj, created = EncryptedRecord.objects.update_or_create(
            patient_name=patient_name,
            defaults={
                'ciphertext': ciphertext,
                'iv'        : iv,
                'wrap_key'  : key,
                'signature' : b'',
            }
        )

        return JsonResponse({
            'status'     : 'success',
            'patient_name': obj.patient_name,
            'created'    : created
        })
    return JsonResponse({'error': 'Only POST allowed'}, status=405)


@csrf_exempt
def read_encrypted_record(request):
    """
    Endpoint API (curl/Postman) para descifrar un expediente:
    Recibe patient_name y devuelve JSON con plaintext.
    """
    if request.method == 'POST':
        patient_name = request.POST.get('patient_name', '').strip()
        if not patient_name:
            return JsonResponse({'error': 'Missing patient_name'}, status=400)

        try:
            record = EncryptedRecord.objects.get(patient_name=patient_name)
            plaintext = decrypt_record_aes_cbc(
                record.ciphertext, record.wrap_key, record.iv
            )
            return JsonResponse({
                'patient_name': record.patient_name,
                'plaintext'   : plaintext.decode(errors='ignore')
            })
        except EncryptedRecord.DoesNotExist:
            return JsonResponse({'error': 'Record not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Only POST allowed'}, status=405)


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import EncryptedRecord
from .utils.crypto import encrypt_record_aes_cbc, decrypt_record_aes_cbc
import os

@login_required
def create_record_form(request):
    """
    GET:  Muestra el formulario dividido en secciones.
    POST: Recibe campos separados (nombre, dirección, edad, etc.),
          lee lista de tratamientos (fecha+descripción), concatena todo
          en un solo texto con separadores, cifra y guarda.
    """
    if request.method == 'POST':
        # 1) Campos de datos personales
        patient_name     = request.POST.get('patient_name', '').strip()
        address          = request.POST.get('address', '').strip()
        age              = request.POST.get('age', '').strip()
        phone            = request.POST.get('phone', '').strip()

        # 2) Alergias / enfermedades crónicas
        allergies        = request.POST.get('allergies', '').strip()
        chronic_diseases = request.POST.get('chronic_diseases', '').strip()

        # 3) Tratamientos: listas paralelas
        treatment_dates        = request.POST.getlist('treatment_date')
        treatment_descriptions = request.POST.getlist('treatment_desc')

        # Validaciones básicas
        if not patient_name:
            messages.error(request, "El nombre del paciente es obligatorio.")
            return redirect('create_record_form')
        if not address or not age or not phone:
            messages.error(request, "Todos los campos de información personal son obligatorios.")
            return redirect('create_record_form')

        # Construir el bloque "Información Personal"
        personal_info = (
            f"Dirección: {address}\n"
            f"Edad: {age}\n"
            f"Teléfono: {phone}"
        )

        # Construir el bloque "Alergias y Enfermedades Crónicas"
        allergies_block = allergies if allergies else "Ninguna"
        chronic_block   = chronic_diseases if chronic_diseases else "Ninguna"

        # Construir el bloque "Tratamientos"
        if treatment_dates and treatment_descriptions:
            treatment_lines = []
            for date_str, desc in zip(treatment_dates, treatment_descriptions):
                if date_str.strip() and desc.strip():
                    treatment_lines.append(f"- {date_str}: {desc.strip()}")
            if treatment_lines:
                treatment_block = "\n".join(treatment_lines)
            else:
                treatment_block = "Sin tratamientos previos"
        else:
            treatment_block = "Sin tratamientos previos"

        # Concatenar todo en un solo texto
        record_text = (
            f"=== Expediente Clínico de {patient_name} ===\n\n"
            f"1) Información Personal:\n{personal_info}\n\n"
            f"2) Alergias:\n{allergies_block}\n\n"
            f"3) Enfermedades Crónicas:\n{chronic_block}\n\n"
            f"4) Historial de Tratamientos:\n{treatment_block}\n"
        )

        # Cifrar con AES-CBC
        key = os.urandom(32)
        ciphertext, iv = encrypt_record_aes_cbc(record_text.encode(), key)

        # Guardar o actualizar (patient_name es único en el modelo)
        EncryptedRecord.objects.update_or_create(
            patient_name=patient_name,
            defaults={
                'ciphertext': ciphertext,
                'iv': iv,
                'wrap_key': key,
                'signature': b'',
            }
        )

        messages.success(request, f"Expediente de “{patient_name}” guardado correctamente.")
        return redirect('dashboard')

    # Si es GET, muestra el formulario con campos vacíos
    return render(request, 'records/create_record.html')



@login_required
def read_record_form(request):
    """
    GET:  Muestra el formulario para buscar por nombre de paciente.
    POST: Busca el registro por patient_name, lo descifra y despliega.
    """
    context = {}
    if request.method == 'POST':
        patient_name = request.POST.get('patient_name', '').strip()
        if not patient_name:
            messages.error(request, "El nombre del paciente es obligatorio.")
            return redirect('read_record_form')

        try:
            record = EncryptedRecord.objects.get(patient_name=patient_name)
            plaintext = decrypt_record_aes_cbc(
                record.ciphertext, record.wrap_key, record.iv
            ).decode(errors='ignore')

            context['found'] = True
            context['record_data'] = {
                'patient_name': record.patient_name,
                'plaintext'   : plaintext
            }
        except EncryptedRecord.DoesNotExist:
            messages.error(request, f"No existe expediente para «{patient_name}».")
            return redirect('read_record_form')
        except Exception as e:
            messages.error(request, f"Error al descifrar: {e}")
            return redirect('read_record_form')

    return render(request, 'records/read_record.html', context)
