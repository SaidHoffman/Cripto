from django.urls import path
from .views import (
    dashboard,
    create_record_form,
    read_record_form,
    create_encrypted_record,
    read_encrypted_record,
)

urlpatterns = [
    # Interfaz web (requerido login)
    path('dashboard/',            dashboard,            name='dashboard'),
    path('create/form/',          create_record_form,   name='create_record_form'),
    path('read/form/',            read_record_form,     name='read_record_form'),

    # API endpoints para curl/Postman (CSRF exempt)
    path('create/',               create_encrypted_record, name='create_encrypted_record'),
    path('read/',                 read_encrypted_record,   name='read_encrypted_record'),
]
