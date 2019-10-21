from django.db import models
from apps.authentication.models import User
from django.urls import reverse


class Classroom(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='classrooms', null=True)
    title = models.CharField(max_length=50)
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
    classroom = models.ForeignKey(Classroom, on_delete=models.SET_NULL, related_name='tasks', null=True)
    date = models.DateTimeField(auto_now_add=True, null=True)

    @property
    def short_text(self):
        return '{}...'.format(self.task_description[:40])

    def get_absolute_url(self):
        return reverse('mine:miner-classroom-task-detail', args=[str(self.classroom.pk),str(self.pk)])

    def __str__(self):
        return '{} - {} - {}'.format(self.pk, self.task_title, self.classroom)


class Miner(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    classroom = models.ManyToManyField(Classroom, related_name='participants', blank=True)
    task = models.ManyToManyField(Task, through='Text')

    def __str__(self):
        return self.user.email


class Text(models.Model):
    content = models.TextField()
    creator = models.ForeignKey(Miner, on_delete=models.CASCADE, related_name='completed_tasks')
    task = models.ForeignKey(Task, on_delete=models.SET_NULL, related_name='completed_tasks', null=True)
    classroom = models.ForeignKey(Classroom, on_delete=models.SET_NULL, related_name='completed_tasks', null=True)
    date = models.DateTimeField(auto_now_add=True, null=True)

    @property
    def short_text(self):
        return '{}...'.format(self.content[:40])

    def get_absolute_url(self):
        return reverse('mine:moderator-classroom-text-moderate', args=[str(self.classroom.pk),str(self.pk)])

    def __str__(self):
        if self.task is None:
            return '{} - {}'.format(self.pk, self.creator.user.email)
        return '{} - {} - {}'.format(self.pk, self.creator.user.email, self.task.pk)


class ModeratedText(models.Model):
    content = models.TextField()
    original = models.ForeignKey(Text, on_delete=models.CASCADE, related_name="moderated_tasks")
    moderator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="moderated_tasks")
    date = models.DateTimeField(auto_now_add=True, null=True)

    @property
    def short_text(self):
        return '{}...'.format(self.content[:40])

    def get_absolute_url(self):
        return reverse('mine:miner-classroom-result-detail', args=[str(self.original.classroom.pk),str(self.original.pk)])

    def __str__(self):
        return '{} - {}'.format(self.pk, self.moderator.email)


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    timestamp = models.DateTimeField(auto_now_add=True)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    description = models.CharField(max_length=100)
    read = models.BooleanField(default=False)

    def __str__(self):
        return '{} - {}'.format(self.user.email, self.description)