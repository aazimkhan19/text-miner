from braces.views import GroupRequiredMixin as BaseGroupRequiredMixin, SuperuserRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.db.models import Count, Q
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, DetailView, UpdateView, FormView, RedirectView

from apps.authentication.forms import ProfileForm
from apps.mine.forms import TextForm, ModerateTextForm, CreateTaskForm, CreateClassroomForm, JoinClassroomForm
from apps.mine.models import Text, ModeratedText, Task, Classroom, Notification, Miner
from apps.mine.task import send_email
from config.settings.common import EMAIL_HOST_USER


# region Base
class BaseTextCreateView(CreateView):
    form_class = TextForm

    def form_valid(self, form):
        """If the form is valid, save the associated model."""
        self.object = form.save()
        self.object.creator = self.request.user.miner
        self.object.task = Task.objects.get(pk=self.kwargs['tpk'])
        self.object.classroom = Classroom.objects.get(pk=self.kwargs['cpk'])
        self.object.save()
        self.configure_email(self.object.classroom, self.object)
        self.configure_notification(self.object.classroom)
        return super().form_valid(form)

    def configure_email(self, classroom, text):
        name = classroom.owner.first_name
        subject = 'Жаңа эссе жіберілді'
        title = '{} {}'.format(text.creator.user.first_name, text.creator.user.last_name)
        message = '{} сыныбында жаңа эссе жіберілді'.format(classroom.title)
        url = self.request.META['HTTP_HOST'] + text.get_absolute_url()
        recipient = [classroom.owner.email]
        send_email(name, subject, title, message, url, recipient)

    def configure_notification(self, classroom):
        message = '{} сыныбында жаңа эссе жіберілді'.format(classroom.title)
        Notification.objects.create(user=classroom.owner,
                                    link=self.object.get_absolute_url(),
                                    description=message)


class BaseMinerView(BaseGroupRequiredMixin):
    group_required = 'miner'
# endregion Base


# region MinerInitial
# Refactor this duplicates classroom code. Consider abstraction
class MinerInitialView(BaseMinerView, DetailView):
    template_name = 'mine/miner/main_tasks.html'
    model = Classroom
    app_superuser = EMAIL_HOST_USER

    def get_queryset(self):
        return Classroom.objects.filter(owner__email=self.app_superuser)

    def get_context_data(self, **kwargs):
        classroom = self.get_object()
        miner = self.request.user.miner
        texts = miner.task.all().filter(classroom=classroom).values_list('pk', flat=True)
        context = {'tasks': classroom.tasks.order_by('-date').exclude(pk__in=texts)}
        kwargs.update(context)
        return super().get_context_data(**kwargs)


# Refactor this duplicates classroom code. Consider abstraction
class MinerResultsInitialView(BaseMinerView, DetailView):
    template_name = 'mine/miner/main_results.html'
    model = Classroom
    app_superuser = EMAIL_HOST_USER

    def get_queryset(self):
        return Classroom.objects.filter(owner__email=self.app_superuser)

    def get_context_data(self, **kwargs):
        classroom = self.get_object()
        miner = self.request.user.miner
        texts = miner.completed_tasks.filter(task__classroom=classroom).order_by('-date')
        context = {'texts': texts}
        kwargs.update(context)
        return super().get_context_data(**kwargs)


# Refactor this duplicates classroom code. Consider abstraction
class MinerTaskDetailView(BaseMinerView, CreateView, DetailView):
    template_name = 'mine/miner/main_task.html'
    pk_url_kwarg = 'tpk'
    form_class = TextForm
    model = Task

    def form_valid(self, form):
        self.object = form.save()
        self.object.creator = self.request.user.miner
        self.object.task = Task.objects.get(pk=self.kwargs['tpk'])
        self.object.classroom = Classroom.objects.get(pk=self.kwargs['pk'])
        self.object.save()
        return super().form_valid(form)

    def get(self, request, *args, **kwargs):
        task = self.get_object()
        miner = self.request.user.miner
        texts = task.completed_tasks.filter(creator=miner)
        if texts.exists():
            text = texts.first()
            return HttpResponseRedirect(
                reverse_lazy('mine:miner-result-detail', kwargs={'pk': kwargs['pk'], 'tpk': text.pk}))

        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return Task.objects.filter(classroom__pk=self.kwargs['pk'])

    def get_success_url(self, **kwargs):
        return reverse_lazy('mine:miner-tasks', kwargs={'pk': self.kwargs['pk']})


# Refactor this duplicates classroom code. Consider abstraction
class MinerResultDetailView(BaseMinerView, DetailView):
    template_name = 'mine/miner/main_result.html'
    pk_url_kwarg = 'tpk'
    model = Text

    def get_context_data(self, **kwargs):
        try:
            moderated_text = ModeratedText.objects.get(original__pk=self.kwargs['tpk'])
            context = {'moderated': True, 'moderated_text': moderated_text}
        except ModeratedText.DoesNotExist:
            context = {'moderated': False}
        kwargs.update(context)
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        classroom = get_object_or_404(Classroom, pk=self.kwargs['pk'])
        miner = self.request.user.miner
        texts = miner.completed_tasks.filter(task__classroom=classroom)
        return texts

    def get_success_url(self, **kwargs):
        return reverse_lazy('mine:miner-tasks', kwargs={'pk': self.kwargs['pk']})
# endregion MinerInitial


# region MinerPersonal
class MinerProfileView(BaseMinerView, UpdateView):
    form_class = ProfileForm
    success_url = reverse_lazy('mine:miner-profile')
    template_name = 'mine/miner/profile.html'

    def get_object(self, queryset=None):
        return self.request.user


class MinerNotificationsView(BaseMinerView, ListView):
    model = Notification
    context_object_name = 'notifications'


class MinerUnreadNotificationsView(MinerNotificationsView):
    template_name = 'mine/miner/notifications_unread.html'

    def get_queryset(self):
        return self.request.user.notifications.filter(read=False).order_by('-date')


class MinerReadNotificationsView(MinerNotificationsView):
    template_name = 'mine/miner/notifications_read.html'

    def get_queryset(self):
        return self.request.user.notifications.filter(read=True).order_by('-date')


class MinerNotificationToggleView(BaseMinerView, RedirectView):
    url = reverse_lazy('mine:miner-notifications-unread')

    def get(self, request, *args, **kwargs):
        notifications = Notification.objects.filter(pk=kwargs['pk'])
        if notifications.exists():
            notification = notifications.first()
            unread_url = reverse_lazy('mine:miner-notifications-unread')
            read_url = reverse_lazy('mine:miner-notifications-read')
            self.url = read_url if notification.read else unread_url
            notification.read = not notification.read
            notification.save()
        return super().get(request, *args, **kwargs)
# endregion MinerPersonal


# region Classroom
class MinerClassroomJoinView(BaseMinerView, FormView):
    form_class = JoinClassroomForm
    template_name = "mine/miner/classroom_join.html"

    def form_valid(self, form):
        Miner.objects.filter(user=self.request.user).first().classroom.add(form.cleaned_data['invitation_code'])
        return HttpResponseRedirect(
            reverse_lazy('mine:miner-classroom-detail', kwargs={'pk': form.cleaned_data['invitation_code'].pk}))


class MinerClassroomListView(BaseMinerView, ListView):
    model = Classroom
    context_object_name = 'classrooms'
    template_name = "mine/miner/classroom_list.html"

    def get_queryset(self):
        miner = self.request.user.miner
        return self.request.user.miner.classroom.all() \
            .annotate(badge=Count('tasks', distinct=True) - Count('completed_tasks', filter=Q(completed_tasks__creator=miner), distinct=True))


class BaseClassroomDetailView(DetailView):
    model = Classroom
    context_object_name = 'classroom'

    def get_queryset(self):
        return self.request.user.miner.classroom.all()


class MinerClassroomDetailView(BaseMinerView, BaseClassroomDetailView):
    template_name = "mine/miner/classroom.html"

    def get_context_data(self, **kwargs):
        classroom = self.get_object()
        miner = self.request.user.miner
        texts = miner.task.all().filter(classroom=classroom).values_list('pk', flat=True)
        context = {'tasks': classroom.tasks.order_by('-date').exclude(pk__in=texts)}
        kwargs.update(context)
        return super().get_context_data(**kwargs)


class MinerClassroomResultsView(BaseMinerView, BaseClassroomDetailView):
    template_name = 'mine/miner/classroom_result.html'

    def get_context_data(self, **kwargs):
        classroom = self.get_object()
        miner = self.request.user.miner
        texts = miner.completed_tasks.filter(task__classroom=classroom).order_by('-date')
        context = {'texts': texts}
        kwargs.update(context)
        return super().get_context_data(**kwargs)


class MinerClassroomTaskDetailView(BaseMinerView, BaseTextCreateView, DetailView):
    model = Task
    context_object_name = 'task'
    pk_url_kwarg = 'tpk'
    template_name = 'mine/miner/task_detail.html'

    def get_queryset(self):
        return get_object_or_404(Classroom, pk=self.kwargs['cpk']).tasks.all()

    def get_success_url(self, **kwargs):
        return reverse_lazy('mine:miner-classroom-detail', kwargs={'pk': self.kwargs['cpk']})

    def get(self, request, *args, **kwargs):
        task = self.get_object()
        miner = self.request.user.miner
        texts = task.completed_tasks.filter(creator=miner)
        if texts.exists():
            text = texts.first()
            return HttpResponseRedirect(
                reverse_lazy('mine:miner-classroom-result-detail', kwargs={'cpk': kwargs['cpk'], 'tpk':text.pk}))

        return super().get(request, *args, **kwargs)


class MinerClassroomResultDetailView(BaseMinerView, DetailView):
    model = Text
    context_object_name = 'text'
    pk_url_kwarg = 'tpk'
    template_name = 'mine/miner/task_result.html'

    def get_queryset(self):
        classroom = get_object_or_404(Classroom, pk=self.kwargs['cpk'])
        miner = self.request.user.miner
        texts = miner.completed_tasks.filter(task__classroom=classroom)
        return texts

    def get_context_data(self, **kwargs):
        try:
            moderated_text = ModeratedText.objects.get(original__pk=self.kwargs['tpk'])
            context = {'moderated': True, 'moderated_text': moderated_text}
        except ModeratedText.DoesNotExist:
            context = {'moderated': False}
        kwargs.update(context)
        return super().get_context_data(**kwargs)
# endregion Classroom
