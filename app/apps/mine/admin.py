from django.contrib import admin

from apps.mine.models import Text
from apps.mine.models import ModeratedText
from apps.mine.models import Task


@admin.register(Text, ModeratedText, Task)
class BasicAdmin(admin.ModelAdmin):
    pass
