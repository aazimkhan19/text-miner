# Generated by Django 2.0 on 2019-10-07 16:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mine', '0020_auto_20191005_0153'),
    ]

    operations = [
        migrations.AddField(
            model_name='text',
            name='classroom',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='mine.Classroom'),
        ),
    ]
