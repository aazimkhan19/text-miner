from django.contrib import admin

from apps.mine.models import Text, ModeratedText, Task, Classroom, Notification, Miner


@admin.register(Text, ModeratedText, Task, Classroom, Notification, Miner)
class BasicAdmin(admin.ModelAdmin):
    pass
