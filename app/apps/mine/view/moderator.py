from braces.views import GroupRequiredMixin as BaseGroupRequiredMixin, SuperuserRequiredMixin
from django.http import Http404

from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView, ListView, DetailView, RedirectView, UpdateView

from django.db.models import Avg, Count

from apps.authentication.forms import ProfileForm
from apps.authentication.models import User
from apps.mine.forms import TextForm, ModerateTextForm, CreateTaskForm, CreateClassroomForm, JoinClassroomForm
from apps.mine.models import Text, ModeratedText, Task, Classroom

from nanoid import generate


class BaseTextModerationView(CreateView):
    form_class = ModerateTextForm
    template_name = None
    success_url = None
    initial_text = None

    def get(self, request, *args, **kwargs):
        self.get_initial_text(kwargs.get('pk'))
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.get_initial_text(kwargs.get('pk'))
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
        self.object.raw_text = self.initial_text
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


class BaseClassroomCreateView(CreateView):
    form_class = CreateClassroomForm

    def form_valid(self, form):
        self.object = form.save()
        self.object.owner = self.request.user
        self.object.invitation_code = generate(size=8)
        self.object.save()
        return super().form_valid(form)


class BaseModeratorView(BaseGroupRequiredMixin):
    group_required = 'moderator'


class ModeratorInitialView(BaseModeratorView, TemplateView):
    template_name = 'mine/moderator/initial.html'


class ModeratorRawTextListView(BaseModeratorView, ListView):
    template_name = 'mine/moderator/raw_texts.html'
    queryset = Text.objects.all()


class ModeratorRawTextDetailView(BaseModeratorView, DetailView):
    queryset = Text.objects.all()
    template_name = 'mine/moderator/raw_text.html'


class ModeratorModerateTextView(BaseModeratorView, BaseTextModerationView):
    template_name = 'mine/moderator/text_moderate.html'
    success_url = reverse_lazy('mine:moderator-moderated-text')


class ModeratorModeratedTextListView(BaseModeratorView, ListView):
    template_name = 'mine/moderator/moderated_texts.html'
    queryset = ModeratedText.objects.all()

    def get_queryset(self):
        return self.queryset.filter(moderator=self.request.user)


class ModeratorModeratedTextDetailView(BaseModeratorView, DetailView):
    template_name = 'mine/moderator/moderated_text.html'
    queryset = ModeratedText.objects.all()

    def get_queryset(self):
        return self.queryset.filter(moderator=self.request.user)


class ModeratorProfileView(BaseModeratorView, UpdateView):
    form_class = ProfileForm
    template_name = 'mine/moderator/profile.html'
    success_url = reverse_lazy('mine:moderator-profile')

    def get_object(self, queryset=None):
        return self.request.user


class ModeratorTaskCreateView(BaseModeratorView, BaseTaskCreateView):
    template_name = "mine/moderator/create_task.html"

    def get_success_url(self):
        return reverse_lazy('mine:moderator-task', kwargs = {'pk' : self.object.pk, })


class ModeratorTaskDetailView(BaseModeratorView, DetailView):
    template_name = 'mine/moderator/task_detail.html'
    queryset = Task.objects.all()


class ModeratorTaskListView(BaseModeratorView, DetailView):
    pass


class ModeratorClassroomCreateView(BaseModeratorView, BaseClassroomCreateView):
    template_name = "mine/moderator/create_task.html"

    def get_success_url(self):
        return reverse_lazy('mine:moderator-classroom-detail', kwargs = {'pk': self.object.pk})


class ModeratorClassroomListView(BaseModeratorView, ListView):
    template_name = "mine/moderator/classroom_list.html"
    model = Classroom
    context_object_name = 'classrooms'

    def get_queryset(self):
        print("DEBUG", self.request.user.classrooms.all())
        return self.request.user.classrooms \
            .annotate(tasks_count = Count('tasks', distinct=True)) \
            .annotate(participants_count = Count('participant', distinct=True))


class ModeratorClassroomDetailView(BaseModeratorView, DetailView):
    template_name = "mine/moderator/classroom.html"
    model = Classroom
    context_object_name = 'classroom'

    def get_queryset(self):
        return self.request.user.classrooms


class ModeratorClassroomTaskCreateView(BaseModeratorView, BaseTaskCreateView):
    template_name = "mine/moderator/create_task.html"

    def get_success_url(self):
        return reverse_lazy('mine:moderator-classroom-detail', kwargs = {'pk' : self.kwargs['pk'], })


class ModeratorRemoveUserView(BaseModeratorView, RedirectView):
    def get(self, request, *args, **kwargs):
        user = User.objects.filter(pk=kwargs['upk'])
        if user.exists():
            Classroom.objects.filter(pk=kwargs['cpk']).first().participants.remove(user.first())
        return super().get(request, *args, **kwargs)

    def get_redirect_url(self, *args, **kwargs):
        return reverse_lazy('mine:moderator-classroom-detail', kwargs={'pk': kwargs['cpk']})
