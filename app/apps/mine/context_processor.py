from django.http import request
from apps.mine.models import Classroom
from config.settings.common import EMAIL_HOST_USER

app_superuser = EMAIL_HOST_USER


def main_classrooms(request):
    classrooms = Classroom.objects.filter(owner__email=app_superuser).order_by('pk').values_list('pk', 'title')
    return {'main_classrooms': classrooms}
