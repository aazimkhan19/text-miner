from django.db import models
from apps.authentication.models import User

class Classroom(models.Model):
    title = models.CharField(max_length=50)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    participants = models.ManyToManyField(User, related_name='participants', blank=True)
    invitation_code = models.CharField(max_length=8, unique=True)

    def __str__(self):
        return '{} - {} - {}'.format(self.pk, self.title, self.owner.email)

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
    task_title = models.CharField(max_length=50, null=True)
    task_description = models.TextField()
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, related_name='tasks',null=True)

    @property
    def short_text(self):
        return '{}...'.format(self.task_description[:40])

    def __str__(self):
        return '{} - {} - {}'.format(self.pk, self.task_level, self.task_title)

class Text(models.Model):
    content = models.TextField()
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True)
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, related_name='completed_tasks', null=True)

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


class CompletedTask(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return '{} - {}'.format(self.task, self.user)