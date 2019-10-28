from braces.views import GroupRequiredMixin as BaseGroupRequiredMixin, SuperuserRequiredMixin
from django.http import Http404
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from django.views.generic import CreateView, ListView, DetailView, RedirectView, UpdateView
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count

from apps.authentication.forms import ProfileForm
from apps.authentication.models import User
from apps.mine.forms import TextForm, ModerateTextForm, CreateTaskForm, CreateClassroomForm, JoinClassroomForm, ModifyTaskForm
from apps.mine.models import Text, ModeratedText, Task, Classroom, Notification
from apps.mine.task import send_email, send_emails, send_mass_notification

from nanoid import generate


# region Base
class BaseTextModerationView(CreateView):
    form_class = ModerateTextForm
    pk_url_kwarg = 'tpk'
    template_name = None
    success_url = None
    initial_text = None

    def get(self, request, *args, **kwargs):
        self.get_initial_text(kwargs.get(self.pk_url_kwarg))
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.get_initial_text(kwargs.get(self.pk_url_kwarg))
        return super().post(request, *args, **kwargs)

    def get_initial_text(self, pk):
        text = Text.objects.filter(pk=pk)
        if not text.exists():
            raise Http404
        self.initial_text = text.first()

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.request.method == 'GET':
            kwargs.update({'initial_text': self.initial_text.content})
        return kwargs

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.original = self.initial_text
        self.object.moderator = self.request.user
        self.object.save()
        self.configure_email(self.object.original.classroom, self.object)
        self.configure_notification(self.object.original.classroom, self.object)
        return super().form_valid(form)

    def configure_email(self, classroom, moderated_text):
        name = moderated_text.original.creator.user.first_name
        subject = 'Your text is moderated'
        title = classroom.title
        message = 'Your essay have been checked'
        url = self.request.META['HTTP_HOST'] + moderated_text.get_absolute_url()
        recipient = [moderated_text.original.creator.user.email]
        send_email.delay(name, subject, title, message, url, recipient)

    def configure_notification(self, classroom, moderated_text):
        message = 'Your essay have been checked in {}'.format(classroom.title)
        Notification.objects.create(user=moderated_text.original.creator.user,
                                    link=self.object.get_absolute_url(),
                                    description=message)


class BaseTaskCreateView(CreateView):
    form_class = CreateTaskForm

    def form_valid(self, form):
        self.object = form.save()
        self.object.classroom = Classroom.objects.get(pk=self.kwargs['pk'])
        self.object.save()
        self.configure_email(self.object.classroom, self.object)
        self.configure_notification(self.object.classroom, self.object)
        return super().form_valid(form)

    def configure_email(self, classroom, task):
        url = self.request.META['HTTP_HOST'] + task.get_absolute_url()
        send_emails.delay(classroom.pk, task.pk, url)

    def configure_notification(self, classroom, task):
        message = 'New task added in {}'.format(classroom.title)
        url = task.get_absolute_url()
        send_mass_notification.delay(classroom.pk, message, url)


class BaseModeratorView(BaseGroupRequiredMixin):
    group_required = 'moderator'
# endregion Base


# region Personal
class ModeratorProfileView(BaseModeratorView, UpdateView):
    form_class = ProfileForm
    success_url = reverse_lazy('mine:moderator-profile')
    template_name = 'mine/moderator/profile.html'

    def get_object(self, queryset=None):
        return self.request.user


class ModeratorNotificationsView(BaseModeratorView, ListView):
    model = Notification
    context_object_name = 'notifications'


class ModeratorUnreadNotificationsView(ModeratorNotificationsView):
    template_name = 'mine/moderator/notifications_unread.html'

    def get_queryset(self):
        return self.request.user.notifications.filter(read=False).order_by('-date')


class ModeratorReadNotificationsView(ModeratorNotificationsView):
    template_name = 'mine/moderator/notifications_read.html'

    def get_queryset(self):
        return self.request.user.notifications.filter(read=True).order_by('-date')


class ModeratorNotificationToggleView(BaseModeratorView, RedirectView):
    url = reverse_lazy('mine:moderator-notifications-unread')

    def get(self, request, *args, **kwargs):
        notifications = Notification.objects.filter(pk=kwargs['pk'])
        if notifications.exists():
            notification = notifications.first()
            unread_url = reverse_lazy('mine:moderator-notifications-unread')
            read_url = reverse_lazy('mine:moderator-notifications-read')
            self.url = read_url if notification.read else unread_url
            notification.read = not notification.read
            notification.save()
        return super().get(request, *args, **kwargs)
# endregion Personal


# region Classroom
class ModeratorClassroomCreateView(BaseModeratorView, CreateView):
    form_class = CreateClassroomForm
    template_name = "mine/moderator/classroom_create.html"

    def form_valid(self, form):
        self.object = form.save()
        self.object.owner = self.request.user
        self.object.invitation_code = generate(size=8)
        self.object.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('mine:moderator-classroom-detail', kwargs={'pk': self.object.pk})


class ModeratorClassroomListView(BaseModeratorView, ListView):
    model = Classroom
    context_object_name = 'classrooms'
    template_name = "mine/moderator/classroom_list.html"

    def get_queryset(self):
        return self.request.user.classrooms \
            .annotate(tasks_count=Count('tasks', distinct=True)) \
            .annotate(participants_count=Count('participants', distinct=True))


class ModeratorClassroomDetailView(BaseModeratorView, DetailView):
    model = Classroom
    context_object_name = 'classroom'
    template_name = "mine/moderator/classroom.html"

    def get_queryset(self):
        return self.request.user.classrooms

    def get_context_data(self, **kwargs):
        classroom = self.get_object()

        tasks = Task.objects.filter(classroom=classroom).order_by('-date')
        moderated_texts = ModeratedText.objects.filter(original__task__classroom=classroom).order_by('-date')
        texts = Text.objects.filter(task__classroom=classroom).order_by('-date').exclude(
            pk__in=moderated_texts.values_list('original__pk', flat=True))
        participants = classroom.participants.all().order_by('user__first_name', 'user__last_name')

        paginator = Paginator(tasks, 5)
        page = self.request.GET.get('task')
        try:
            tasks = paginator.page(page)
        except (PageNotAnInteger, EmptyPage):
            tasks = paginator.page(1)

        paginator = Paginator(texts, 10)
        page = self.request.GET.get('text')
        try:
            texts = paginator.page(page)
        except(PageNotAnInteger, EmptyPage):
            texts = paginator.page(1)

        paginator = Paginator(moderated_texts, 5)
        page = self.request.GET.get('moderated')
        try:
            moderated_texts = paginator.page(page)
        except(PageNotAnInteger, EmptyPage):
            moderated_texts = paginator.page(1)

        context = {
            'tasks': tasks,
            'texts': texts,
            'moderated_texts': moderated_texts,
            'participants': participants
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)


class ModeratorClassroomTaskCreateView(BaseModeratorView, BaseTaskCreateView):
    template_name = "mine/moderator/task_create.html"

    def get_context_data(self, **kwargs):
        classroom = get_object_or_404(Classroom, pk=self.kwargs['pk'])
        context = {'classroom': classroom}
        kwargs.update(context)
        return super().get_context_data(**kwargs)

    def get_success_url(self):
        return reverse_lazy('mine:moderator-classroom-detail', kwargs={'pk': self.kwargs['pk'], })


class ModeratorClassroomTaskEditView(BaseModeratorView, UpdateView):
    form_class = ModifyTaskForm
    context_object_name = 'task'
    pk_url_kwarg = 'tpk'
    template_name = 'mine/moderator/task_modify.html'

    def get_queryset(self):
        return Classroom.objects.get(pk=self.kwargs['cpk']).tasks.all()

    def get_success_url(self):
        return reverse_lazy('mine:moderator-classroom-detail', kwargs={'pk': self.kwargs['cpk'], })


class ModeratorClassroomTaskRemoveView(BaseModeratorView, RedirectView):
    def get(self, request, *args, **kwargs):
        tasks = Task.objects.filter(pk=kwargs['tpk'])
        if tasks.exists():
            task = tasks.first()
            task.delete()
        return super().get(request, *args, **kwargs)

    def get_redirect_url(self, *args, **kwargs):
        return reverse_lazy('mine:moderator-classroom-detail', kwargs={'pk': self.kwargs['cpk']})


class ModeratorClassroomModerateTextView(BaseModeratorView, BaseTextModerationView, DetailView):
    model = Text
    context_object_name = 'text'
    template_name = 'mine/moderator/text_moderate.html'

    def get_queryset(self):
        return Text.objects.filter(task__classroom__pk=self.kwargs['cpk'])

    def get_success_url(self):
        return reverse_lazy('mine:moderator-classroom-detail', kwargs={'pk': self.kwargs['cpk']})


class ModeratorClassroomModeratedTextView(BaseModeratorView, DetailView):
    model = Text
    context_object_name = 'moderated_text'
    pk_url_kwarg = 'tpk'
    template_name = 'mine/moderator/text_moderated.html'

    def get_queryset(self):
        return ModeratedText.objects.filter(original__task__classroom__pk=self.kwargs['cpk'])


class ModeratorRemoveUserView(BaseModeratorView, RedirectView):
    def get(self, request, *args, **kwargs):
        user = User.objects.filter(pk=kwargs['upk'])
        if user.exists():
            miner = user.first().miner
            Classroom.objects.get(pk=kwargs['cpk']).participants.remove(miner)
        return super().get(request, *args, **kwargs)

    def get_redirect_url(self, *args, **kwargs):
        return reverse_lazy('mine:moderator-classroom-detail', kwargs={'pk': self.kwargs['cpk']})
# endregion Classroom
