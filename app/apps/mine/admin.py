from django.contrib import admin

from apps.mine.models import Text, ModeratedText, Task, Classroom, CompletedTask


@admin.register(Text, ModeratedText, Task, Classroom, CompletedTask)
class BasicAdmin(admin.ModelAdmin):
    pass
