# Generated by Django 2.0 on 2019-12-08 15:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mine', '0041_auto_20191206_1256'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='task_level',
            field=models.CharField(choices=[('BEGINNER', 'Қарапайым деңгей'), ('INTERMEDIATE', 'Орта деңгей'), ('ADVANCED', 'Күрделі деңгей')], default='BEGINNER', max_length=12),
        ),
    ]