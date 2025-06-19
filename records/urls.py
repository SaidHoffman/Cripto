from django.urls import path
from django.contrib.auth import views as auth_views
from .views import (
    dashboard,
    create_record_form,
    read_record_form,
    create_encrypted_record,
    read_encrypted_record,
    generate_keys,
    user_settings,
)

urlpatterns = [
    path('dashboard/',            dashboard,            name='dashboard'),
    path('create/form/',          create_record_form,   name='create_record_form'),
    path('read/form/',            read_record_form,     name='read_record_form'),
    path('create/',               create_encrypted_record, name='create_encrypted_record'),
    path('read/',                 read_encrypted_record,   name='read_encrypted_record'),
    path('generate-keys/',        generate_keys,        name='generate_keys'),
    path('settings/',             user_settings,        name='user_settings'),

    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='registration/password_reset_form.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name='password_reset_complete'),

]
