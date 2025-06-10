from django.http import JsonResponse
from .utils.crypto import generate_ed25519_keypair, generate_x25519_keypair
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
import io
import zipfile
from .models import EncryptedRecord, UserKeys
from .utils.crypto import encrypt_record_aes_cbc, decrypt_record_aes_cbc, sign_record, extract_signature_and_plaintext, verify_signature 
from django.utils import timezone
import os



@login_required
def dashboard(request):
    user = request.user 
    recent_records = EncryptedRecord.objects.order_by('-timestamp')[:5]
    total_patients = EncryptedRecord.objects.count()
    now = timezone.now()
    monthly_records = EncryptedRecord.objects.filter(timestamp__month=now.month,timestamp__year=now.year).count()


    has_keys = False
    if hasattr(user, 'keys'):
        if user.keys.public_signing_key and user.keys.public_encryption_key:
            has_keys = True

    return render(request, 'records/dashboard.html', {
        'recent_records': recent_records,
        'total_patients': total_patients,
        'monthly_records': monthly_records,
        'has_keys': has_keys,
    })

def home(request):
    return render(request, 'home.html') 


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

        key = os.urandom(32) 
        ciphertext, iv = encrypt_record_aes_cbc(record_data, key)

        # Guardar o actualizar (si ya existe nombre, lo reemplaza)
        obj, created = EncryptedRecord.objects.update_or_create(
            patient_name=patient_name,
            defaults={
                'ciphertext': ciphertext,
                'iv'        : iv,
                'wrap_key'  : key,
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
    Recibe patient_name y devuelve JSON con plaintext y estado de la firma.
    """
    if request.method == 'POST':
        patient_name = request.POST.get('patient_name', '').strip()
        if not patient_name:
            return JsonResponse({'error': 'Missing patient_name'}, status=400)

        try:
            record = EncryptedRecord.objects.get(patient_name=patient_name)

            # Desencriptar
            signed_data = decrypt_record_aes_cbc(record.ciphertext, record.wrap_key, record.iv)

            # Recuperar clave pública del usuario (asumimos que nombre único = dueño)
            user_keys = UserKeys.objects.get(user__encryptedrecord=record)
            public_key = user_keys.public_signing_key

            # Verificar firma
            is_valid = verify_signature(public_key, signed_data)
            _, plaintext = extract_signature_and_plaintext(signed_data)

            return JsonResponse({
                'patient_name': record.patient_name,
                'plaintext': plaintext.decode(errors='ignore'),
                'signature_valid': is_valid
            })

        except EncryptedRecord.DoesNotExist:
            return JsonResponse({'error': 'Record not found'}, status=404)
        except UserKeys.DoesNotExist:
            return JsonResponse({'error': 'Public key not found for this record'}, status=500)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Only POST allowed'}, status=405)



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

        # 1) Leer clave privada del archivo .key
        private_key_file = request.FILES.get('private_key_file')
        if not private_key_file:
            messages.error(request, "Debes subir tu clave privada para firmar.")
            return redirect('create_record_form')

        private_key_bytes = private_key_file.read()
        if len(private_key_bytes) != 32:
            messages.error(request, "La clave privada debe tener exactamente 32 bytes (Ed25519 en formato raw).")
            return redirect('create_record_form')

        # 2) Firmar el expediente
        signed_data = sign_record(record_text.encode(), private_key_bytes)  # output: firma (64) + texto

        # 3) Cifrar con AES-CBC
        key = os.urandom(32)
        ciphertext, iv = encrypt_record_aes_cbc(signed_data, key)


        # Guardar o actualizar (patient_name es único en el modelo)
        EncryptedRecord.objects.update_or_create(
            patient_name=patient_name,
            defaults={
                'user': request.user,
                'ciphertext': ciphertext,
                'iv': iv,
                'wrap_key': key,
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
    POST: Busca el registro por patient_name, lo descifra, verifica la firma y despliega.
    """
    context = {}
    if request.method == 'POST':
        patient_name = request.POST.get('patient_name', '').strip()
        if not patient_name:
            messages.error(request, "El nombre del paciente es obligatorio.")
            return redirect('read_record_form')

        try:
            record = EncryptedRecord.objects.get(patient_name=patient_name)
            signed_data = decrypt_record_aes_cbc(record.ciphertext, record.wrap_key, record.iv)
            now = timezone.now()
            # Recuperar clave pública del firmante
            user_keys = UserKeys.objects.get(user__encryptedrecord=record)
            public_key = user_keys.public_signing_key

            # Verificar firma
            is_valid = verify_signature(public_key, signed_data)
            _, plaintext = extract_signature_and_plaintext(signed_data)

            context['found'] = True
            context['now'] = timezone.now()
            context['record_data'] = {
                'patient_name': record.patient_name,
                'plaintext': plaintext.decode(errors='ignore'),
                'signature_valid': is_valid,
            }

        except EncryptedRecord.DoesNotExist:
            messages.error(request, f"No existe expediente para «{patient_name}».")
            return redirect('read_record_form')
        except UserKeys.DoesNotExist:
            messages.error(request, "No se encontró clave pública para verificar la firma.")
            return redirect('read_record_form')
        except Exception as e:
            messages.error(request, f"Error al descifrar: {e}")
            return redirect('read_record_form')

    return render(request, 'records/read_record.html', context)

@login_required
def generate_keys(request):
    user = request.user

    if hasattr(user, 'keys') and user.keys.public_signing_key and user.keys.public_encryption_key:
        return HttpResponse("Ya tienes claves generadas.", status=400)

    # Llama funciones del módulo utils.crypto
    ed_priv, ed_pub = generate_ed25519_keypair()
    x_priv, x_pub = generate_x25519_keypair()

    # Guardar públicas
    user_keys, created = UserKeys.objects.get_or_create(user=user)
    user_keys.public_signing_key = ed_pub
    user_keys.public_encryption_key = x_pub
    user_keys.save()

    # Preparar archivo .zip
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zip_file:
        zip_file.writestr("clave_privada_firma_ed25519.key", ed_priv)
        zip_file.writestr("clave_publica_firma_ed25519.key", ed_pub)
        zip_file.writestr("clave_privada_cifrado_x25519.key", x_priv)
        zip_file.writestr("clave_publica_cifrado_x25519.key", x_pub)

    zip_buffer.seek(0)
    response = HttpResponse(zip_buffer, content_type="application/zip")
    response['Content-Disposition'] = f'attachment; filename=claves_{user.username}.zip'
    return response
