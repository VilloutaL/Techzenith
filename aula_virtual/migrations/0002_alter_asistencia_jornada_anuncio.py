# Generated by Django 4.1.1 on 2024-07-02 02:05

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('aula_virtual', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='asistencia',
            name='jornada',
            field=models.CharField(choices=[('AM', 'Mañana'), ('PM', 'Tarde')], max_length=2),
        ),
        migrations.CreateModel(
            name='Anuncio',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titulo', models.CharField(max_length=200)),
                ('contenido', models.TextField()),
                ('fecha_publicacion', models.DateTimeField(default=django.utils.timezone.now)),
                ('ultima_actualizacion', models.DateTimeField(auto_now=True)),
                ('esta_eliminado', models.BooleanField(default=False)),
                ('asignatura', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='aula_virtual.asignatura')),
                ('profesor', models.ForeignKey(limit_choices_to={'is_profesor': True}, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
