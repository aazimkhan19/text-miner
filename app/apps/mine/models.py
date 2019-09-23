from django.db import models
from apps.authentication.models import User

class Task(models.Model):
    BEGINNER = 'BEGINNER'
    INTERMEDIATE = 'INTERMEDIATE'
    ADVANCED = 'ADVANCED'
    LEVEL_CHOICES = [
        (BEGINNER, 'Beginner'),
        (INTERMEDIATE, 'Intermediate'),
        (ADVANCED, 'Advanced'),
    ]
    task_level = models.CharField(
        max_length=12,
        choices=LEVEL_CHOICES,
        default=BEGINNER,
    )
    task_description = models.TextField()

    def __str__(self):
        return '{} - {} - {}'.format(self.pk, self.task_level, self.task_description)

class Text(models.Model):
    content = models.TextField()
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True)

    @property
    def short_text(self):
        return '{}...'.format(self.content[:40])

    def __str__(self):
        return '{} - {}'.format(self.pk, self.creator.email)


class ModeratedText(models.Model):
    content = models.TextField()
    raw_text = models.ForeignKey(Text, on_delete=models.CASCADE)
    moderator = models.ForeignKey(User, on_delete=models.CASCADE)

    @property
    def short_text(self):
        return '{}...'.format(self.content[:40])

    def __str__(self):
        return '{} - {}'.format(self.pk, self.moderator.email)