from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings

def assign_user_to_existing_records(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    EncryptedRecord = apps.get_model('records', 'EncryptedRecord')
    default_user = User.objects.first()
    if not default_user:
        raise Exception("Debes tener al menos un usuario antes de migrar.")

    for record in EncryptedRecord.objects.all():
        record.user = default_user
        record.save()

class Migration(migrations.Migration):

    dependencies = [
        ('records', '0002_userkeys'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='encryptedrecord',
            name='user',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.RunPython(assign_user_to_existing_records),
        migrations.AlterField(
            model_name='encryptedrecord',
            name='user',
            field=models.ForeignKey(
                null=False,
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL
            ),
        ),
    ]
