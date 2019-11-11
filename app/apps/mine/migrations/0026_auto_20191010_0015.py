# Generated by Django 2.0 on 2019-10-09 18:15

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0002_auto_20191001_1342'),
        ('mine', '0025_auto_20191009_1613'),
    ]

    operations = [
        migrations.CreateModel(
            name='Miner',
            fields=[
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.RenameField(
            model_name='moderatedtext',
            old_name='raw_text',
            new_name='original',
        ),
        migrations.AddField(
            model_name='moderatedtext',
            name='date',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='task',
            name='date',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='text',
            name='date',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='classroom',
            name='owner',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='classrooms', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='text',
            name='task',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='completed_tasks', to='mine.Task'),
        ),
        migrations.AddField(
            model_name='miner',
            name='classroom',
            field=models.ManyToManyField(related_name='participant', to='mine.Classroom'),
        ),
    ]