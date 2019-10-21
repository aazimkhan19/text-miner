from celery import shared_task

from django.core.mail import send_mail
from django.template.loader import render_to_string

from config.settings.common import EMAIL_HOST_USER
from apps.mine.models import Classroom, Task, Text


@shared_task
def send_email(name, subject, title, message, url, recipient):
    template = render_html_template(name, title, message, url)
    send_mail(subject, message, EMAIL_HOST_USER, recipient, html_message=template)


@shared_task
def send_emails(classroom_pk, task_pk, url):
    classroom = Classroom.objects.get(pk=classroom_pk)
    task = Task.objects.get(pk=task_pk)

    subject = 'New task'
    message = 'new task added in {}'.format(classroom.title)

    for recipient in classroom.participants.all():
        template = render_html_template(recipient.user.first_name, task.task_title, message, url)
        send_mail(subject, message, EMAIL_HOST_USER, [recipient.user.email], html_message=template)


def render_html_template(name, title, text, url):
    context = {
        'name': name,
        'card_title': title,
        'card_text': text,
        'text_url': url
    }
    template = render_to_string('mine/email_body.html', context)
    return template
