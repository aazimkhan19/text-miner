from braces.views import GroupRequiredMixin as BaseGroupRequiredMixin, SuperuserRequiredMixin
from django.http import Http404

from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, DetailView, RedirectView, UpdateView

from django.db.models import Count

from apps.authentication.forms import ProfileForm
from apps.authentication.models import User
from apps.mine.forms import TextForm, ModerateTextForm, CreateTaskForm, CreateClassroomForm, JoinClassroomForm, ModifyTaskForm
from apps.mine.models import Text, ModeratedText, Task, Classroom

from nanoid import generate


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
        return super().form_valid(form)


class BaseTaskCreateView(CreateView):
    form_class = CreateTaskForm

    def form_valid(self, form):
        self.object = form.save()
        self.object.classroom = Classroom.objects.get(pk=self.kwargs['pk'])
        self.object.save()
        return super().form_valid(form)


class BaseModeratorView(BaseGroupRequiredMixin):
    group_required = 'moderator'


class ModeratorProfileView(BaseModeratorView, UpdateView):
    form_class = ProfileForm
    template_name = 'mine/moderator/profile.html'
    success_url = reverse_lazy('mine:moderator-profile')

    def get_object(self, queryset=None):
        return self.request.user


class ModeratorClassroomCreateView(BaseModeratorView, CreateView):
    template_name = "mine/moderator/classroom_create.html"
    form_class = CreateClassroomForm

    def form_valid(self, form):
        self.object = form.save()
        self.object.owner = self.request.user
        self.object.invitation_code = generate(size=8)
        self.object.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('mine:moderator-classroom-detail', kwargs={'pk': self.object.pk})


class ModeratorClassroomListView(BaseModeratorView, ListView):
    template_name = "mine/moderator/classroom_list.html"
    model = Classroom
    context_object_name = 'classrooms'

    def get_queryset(self):
        return self.request.user.classrooms \
            .annotate(tasks_count=Count('tasks', distinct=True)) \
            .annotate(participants_count=Count('participants', distinct=True))


class ModeratorClassroomDetailView(BaseModeratorView, DetailView):
    template_name = "mine/moderator/classroom.html"
    model = Classroom
    context_object_name = 'classroom'

    def get_queryset(self):
        return self.request.user.classrooms

    def get_context_data(self, **kwargs):
        classroom = self.get_object()
        moderated_texts = ModeratedText.objects.filter(original__task__classroom=classroom)
        texts = Text.objects.filter(task__classroom=classroom).exclude(pk__in=moderated_texts.values_list('original__pk', flat=True))
        context = {'texts': texts, 'moderated_texts': moderated_texts}
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
    template_name = 'mine/moderator/task_modify.html'
    form_class = ModifyTaskForm
    context_object_name = 'task'
    pk_url_kwarg = 'tpk'

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
    template_name = 'mine/moderator/text_moderate.html'
    model = Text
    context_object_name = 'text'

    def get_queryset(self):
        return Text.objects.filter(task__classroom__pk=self.kwargs['cpk'])

    def get_success_url(self):
        return reverse_lazy('mine:moderator-classroom-detail', kwargs={'pk': self.kwargs['cpk']})


class ModeratorClassroomModeratedTextView(BaseModeratorView, DetailView):
    template_name = 'mine/moderator/text_moderated.html'
    model = Text
    context_object_name = 'moderated_text'
    pk_url_kwarg = 'tpk'

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
