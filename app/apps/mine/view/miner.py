from braces.views import GroupRequiredMixin as BaseGroupRequiredMixin, SuperuserRequiredMixin
from django.http import HttpResponseRedirect

from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, DetailView, UpdateView, FormView, RedirectView

from apps.authentication.forms import ProfileForm
from apps.mine.forms import TextForm, ModerateTextForm, CreateTaskForm, CreateClassroomForm, JoinClassroomForm
from apps.mine.models import Text, ModeratedText, Task, Classroom, Notification, Miner


class BaseTextCreateView(CreateView):
    form_class = TextForm

    def form_valid(self, form):
        """If the form is valid, save the associated model."""
        self.object = form.save()
        self.object.creator = self.request.user.miner
        self.object.task = Task.objects.get(pk=self.kwargs['tpk'])
        self.object.classroom = Classroom.objects.get(pk=self.kwargs['cpk'])
        self.object.save()
        return super().form_valid(form)


class BaseMinerView(BaseGroupRequiredMixin):
    group_required = 'miner'


class MinerInitialView(BaseMinerView):
    template_name = 'mine/miner/tasks.html'
    paginate_by = 9


class MinerInitialViewBeginner(MinerInitialView, ListView):
    queryset = Task.objects.filter(task_level="BEGINNER")


class MinerInitialViewIntermediate(MinerInitialView, ListView):
    queryset = Task.objects.filter(task_level="INTERMEDIATE")


class MinerInitialViewAdvanced(MinerInitialView, ListView):
    queryset = Task.objects.filter(task_level="ADVANCED")


class MinerTaskDetailView(BaseMinerView, BaseTextCreateView, DetailView):
    template_name = 'mine/miner/task_detail.html'
    queryset = Task.objects.all()

    def get_success_url(self, **kwargs):
        # Костыль, нужно будет потом переделать...
        obj = Task.objects.get(pk=self.kwargs['pk']).task_level
        success_url = ''
        if obj == 'BEGINNER':
            success_url = reverse_lazy('mine:miner-tasks-beginner')
        elif obj == 'INTERMEDIATE':
            success_url = reverse_lazy('mine:miner-tasks-intermediate')
        elif obj == 'ADVANCED':
            success_url = reverse_lazy('mine:miner-tasks-advanced')
        return success_url


class MinerProfileView(BaseMinerView, UpdateView):
    form_class = ProfileForm
    template_name = 'mine/miner/profile.html'
    success_url = reverse_lazy('mine:miner-profile')

    def get_object(self, queryset=None):
        return self.request.user


class MinerNotificationsView(BaseMinerView, ListView):
    template_name = 'mine/miner/notifications.html'
    queryset = Notification.objects.all()

    def get_context_data(self, **kwargs):
        context = super(MinerNotificationsView, self).get_context_data(**kwargs)
        context['read_notifications'] = Notification.objects.filter(read=True)
        context['unread_notifications'] = Notification.objects.filter(read=False)
        return context


class MinerNotificationToggleView(BaseMinerView, RedirectView):
    url = reverse_lazy('mine:miner-notifications')

    def get(self, request, *args, **kwargs):
        notifications = Notification.objects.filter(pk=kwargs['pk'])
        if notifications.exists():
            notification = notifications.first()
            notification.read = not notification.read
            notification.save()
        return super().get(request, *args, **kwargs)


class MinerClassroomJoinView(BaseMinerView, FormView):
    form_class = JoinClassroomForm
    template_name = "mine/miner/join_classroom.html"

    def form_valid(self, form):
        Miner.objects.filter(user=self.request.user).first().classroom.add(form.cleaned_data['invitation_code'])
        return HttpResponseRedirect(
            reverse_lazy('mine:miner-classroom-detail', kwargs={'pk': form.cleaned_data['invitation_code'].pk}))


class MinerClassroomListView(BaseMinerView, ListView):
    template_name = "mine/miner/classroom_list.html"
    model = Classroom
    context_object_name = 'classrooms'

    def get_queryset(self):
        return self.request.user.miner.classroom.all()


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
        context = {'tasks': classroom.tasks.exclude(pk__in=texts)}
        kwargs.update(context)
        return super().get_context_data(**kwargs)


class MinerClassroomResultsView(BaseMinerView, BaseClassroomDetailView):
    template_name = "mine/miner/classroom_result.html"

    def get_context_data(self, **kwargs):
        classroom = self.get_object()
        miner = self.request.user.miner
        texts = miner.completed_tasks.filter(task__classroom=classroom)
        context = {'texts': texts}
        kwargs.update(context)
        return super().get_context_data(**kwargs)


class MinerClassroomTaskDetailView(BaseMinerView, BaseTextCreateView, DetailView):
    template_name = 'mine/miner/task_detail.html'
    model = Task
    pk_url_kwarg = "tpk"

    def get_queryset(self):
        return Classroom.objects.get(pk=self.kwargs['cpk']).tasks.all()

    def get_success_url(self, **kwargs):
        return reverse_lazy('mine:miner-classroom-detail', kwargs={'pk': self.kwargs['cpk']})

    def get(self, request, *args, **kwargs):
        task = self.model.objects.get(pk=kwargs['tpk'])
        miner = self.request.user.miner
        texts = task.completed_tasks.filter(creator=miner)
        if texts.exists():
            text = texts.first()
            return HttpResponseRedirect(
                reverse_lazy('mine:miner-classroom-result-detail', kwargs={'cpk': kwargs['cpk'], 'tpk':text.pk}))

        return super().get(request, *args, **kwargs)


class MinerClassroomResultDetailView(BaseMinerView, DetailView):
    template_name = 'mine/miner/task_result.html'
    model = Text
    pk_url_kwarg = "tpk"

    def get_queryset(self):
        classroom = Classroom.objects.get(pk=self.kwargs['cpk'])
        miner = self.request.user.miner
        texts = miner.completed_tasks.filter(task__classroom=classroom)
        return texts
