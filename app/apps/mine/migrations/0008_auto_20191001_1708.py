# Generated by Django 2.0 on 2019-10-01 11:08

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mine', '0007_task_task_title'),
    ]

    operations = [
        migrations.AlterField(
            model_name='classroom',
            name='owner',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
