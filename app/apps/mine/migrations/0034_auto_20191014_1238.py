# Generated by Django 2.0 on 2019-10-14 06:38

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mine', '0033_auto_20191013_0032'),
    ]

    operations = [
        migrations.AlterField(
            model_name='moderatedtext',
            name='moderator',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='checked_tasks', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='moderatedtext',
            name='original',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='checked_tasks', to='mine.Text'),
        ),
        migrations.AlterField(
            model_name='task',
            name='classroom',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tasks', to='mine.Classroom'),
        ),
        migrations.AlterField(
            model_name='text',
            name='classroom',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='completed_tasks', to='mine.Classroom'),
        ),
        migrations.AlterField(
            model_name='text',
            name='task',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='completed_tasks', to='mine.Task'),
        ),
    ]
