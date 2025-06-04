# records/models.py
from django.db import models

class EncryptedRecord(models.Model):
    patient_name   = models.CharField(max_length=150, unique=True)
    ciphertext     = models.BinaryField()
    iv             = models.BinaryField()
    wrap_key     = models.BinaryField(help_text="Clave simétrica cifrada para el dentista A")
    wrap_key_b     = models.BinaryField(help_text="Clave simétrica cifrada para el dentista B")  
    timestamp      = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.patient_name
