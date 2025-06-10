# records/models.py
from django.contrib.auth.models import User
from django.db import models

class EncryptedRecord(models.Model):
    user            = models.ForeignKey(User, on_delete=models.CASCADE, null=True)  
    patient_name   = models.CharField(max_length=150, unique=True)
    ciphertext     = models.BinaryField()
    iv             = models.BinaryField()
    wrap_key       = models.BinaryField(help_text="Clave simétrica cifrada para el dentista A")
    wrap_key_b     = models.BinaryField(help_text="Clave simétrica cifrada para el dentista B")  
    timestamp      = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.patient_name


class UserKeys(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='keys')
    public_signing_key = models.BinaryField(null=True, blank=True, help_text="Clave pública de firma Ed25519")
    public_encryption_key = models.BinaryField(null=True, blank=True, help_text="Clave pública de cifrado X25519")

    def __str__(self):
        return f"Claves de {self.user.username}"
