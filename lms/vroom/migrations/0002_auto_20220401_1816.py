# Generated by Django 3.2 on 2022-04-01 18:16

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('vroom', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Calificacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nota', models.FloatField(blank=True, default=True, null=True)),
                ('comentario', models.CharField(blank=True, default=None, max_length=500, null=True)),
                ('fecha_calificacion', models.DateTimeField(blank=True, default=None, null=True)),
                ('alumno', models.ForeignKey(default=True, on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
                ('profesor', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='profesor', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Tarea',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titulo', models.CharField(max_length=100)),
                ('descripcion', models.TextField(blank=True, default=None, null=True)),
                ('enunciado', models.TextField()),
                ('nota_maxima', models.FloatField()),
                ('fecha_publicacion', models.DateTimeField(default=django.utils.timezone.now)),
                ('min_exercise_version', models.FloatField(blank=True, default=1.0, null=True)),
                ('autor', models.ForeignKey(default=True, on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
                ('curso', models.ForeignKey(default=True, on_delete=django.db.models.deletion.DO_NOTHING, to='vroom.curso')),
            ],
        ),
        migrations.RemoveField(
            model_name='entrega',
            name='ejercicio',
        ),
        migrations.RemoveField(
            model_name='entrega',
            name='fecha_calificacion',
        ),
        migrations.RemoveField(
            model_name='entrega',
            name='profesor',
        ),
        migrations.RemoveField(
            model_name='pin',
            name='ejercicio',
        ),
        migrations.DeleteModel(
            name='Ejercicio',
        ),
        migrations.DeleteModel(
            name='Tipo_Ejercicio',
        ),
        migrations.AddField(
            model_name='calificacion',
            name='tarea',
            field=models.ForeignKey(default=False, on_delete=django.db.models.deletion.DO_NOTHING, to='vroom.tarea'),
        ),
        migrations.AddField(
            model_name='entrega',
            name='tarea',
            field=models.ForeignKey(default=False, on_delete=django.db.models.deletion.DO_NOTHING, to='vroom.tarea'),
        ),
        migrations.AddField(
            model_name='pin',
            name='tarea',
            field=models.ForeignKey(default=False, on_delete=django.db.models.deletion.DO_NOTHING, to='vroom.tarea'),
        ),
    ]