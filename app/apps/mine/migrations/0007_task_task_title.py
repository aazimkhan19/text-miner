# Generated by Django 2.0 on 2019-09-30 16:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mine', '0006_classroom_classroompeople_classroomtask_completedtask'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='task_title',
            field=models.TextField(max_length=50, null=True),
        ),
    ]