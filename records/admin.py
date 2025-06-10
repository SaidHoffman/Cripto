from django.contrib import admin
from .models import EncryptedRecord, UserKeys

@admin.register(EncryptedRecord)
class EncryptedRecordAdmin(admin.ModelAdmin):
    list_display = ('patient_name', 'user', 'timestamp')  # columnas visibles en el listado
    readonly_fields = ('timestamp',)  # para que no se pueda editar manualmente
    fieldsets = (
        (None, {
            'fields': ('user', 'patient_name', 'ciphertext', 'iv', 'wrap_key', 'wrap_key_b', 'timestamp')
        }),
    )


@admin.register(UserKeys)
class UserKeysAdmin(admin.ModelAdmin):
    list_display = ('user', )
    fieldsets = (
        (None, {
            'fields': ('user', 'public_signing_key', 'public_encryption_key')
        }),
    )
