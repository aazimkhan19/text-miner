from braces.views import GroupRequiredMixin as BaseGroupRequiredMixin, SuperuserRequiredMixin
from django.http import Http404
from django.shortcuts import render
from django.template.loader import render_to_string

from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, DetailView, RedirectView, UpdateView

from django.db.models import Count

from apps.authentication.forms import ProfileForm
from apps.authentication.models import User
from apps.mine.forms import TextForm, ModerateTextForm, CreateTaskForm, CreateClassroomForm, JoinClassroomForm, ModifyTaskForm
from apps.mine.models import Text, ModeratedText, Task, Classroom
from apps.mine.task import send_email, send_emails

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
        return super().form_valid(form)

    def configure_email(self, classroom, moderated_text):
        name = moderated_text.original.creator.user.first_name
        subject = 'Your text is moderated'
        title = classroom.title
        message = 'Your essay have been checked'
        url = self.request.META['HTTP_HOST'] + moderated_text.get_absolute_url()
        recipient = [moderated_text.original.creator.user.email]
        send_email.delay(name, subject, title, message, url, recipient)


class BaseTaskCreateView(CreateView):
    form_class = CreateTaskForm

    def form_valid(self, form):
        self.object = form.save()
        self.object.classroom = Classroom.objects.get(pk=self.kwargs['pk'])
        self.object.save()
        self.configure_email(self.object.classroom, self.object)
        return super().form_valid(form)

    def configure_email(self, classroom, task):
        url = self.request.META['HTTP_HOST'] + task.get_absolute_url()
        send_emails.delay(classroom.pk, task.pk, url)


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
        texts = Text.objects.filter(task__classroom=classroom).order_by('-date').exclude(pk__in=moderated_texts.values_list('original__pk', flat=True))
        participants = classroom.participants.all().order_by('user__first_name', 'user__last_name')
        print('DEBUG', participants)
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
        classroom = Classroom.objects.get(pk=self.kwargs['pk'])
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