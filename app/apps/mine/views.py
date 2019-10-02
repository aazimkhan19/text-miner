from braces.views import GroupRequiredMixin as BaseGroupRequiredMixin, SuperuserRequiredMixin
from django.db.models import Q
from django.http import Http404
from django.shortcuts import redirect, render

from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView, ListView, DetailView, RedirectView, UpdateView

from apps.authentication.forms import ProfileForm
from apps.authentication.models import User
from apps.mine.forms import TextForm, ModerateTextForm, CreateTaskForm, CreateClassroomForm
from apps.mine.models import Text, ModeratedText, Task, Classroom


class BaseTextCreateView(CreateView):
    form_class = TextForm

    def form_valid(self, form):
        """If the form is valid, save the associated model."""
        self.object = form.save()
        self.object.creator = self.request.user
        self.object.task = Task.objects.get(pk=self.kwargs['pk'])
        self.object.save()
        return super().form_valid(form)


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


class BaseClassroomCreateView(CreateView):
    form_class = CreateClassroomForm

    def form_valid(self, form):
        print(self.object)
        self.object = form.save()
        self.object.owner = self.request.user
        self.object.save()
        return super().form_valid(form)


# Admin views
class BaseAdminView(SuperuserRequiredMixin):
    pass


class AdminRawTextListView(BaseAdminView, ListView):
    template_name = 'mine/admin/raw_texts.html'
    queryset = Text.objects.all()


class AdminRawTextCreateView(BaseAdminView, BaseTextCreateView):
    template_name = 'mine/admin/raw_text_create.html'
    success_url = reverse_lazy('mine:admin-raw-texts')


class AdminRawTextDetailView(BaseAdminView, DetailView):
    queryset = Text.objects.all()
    template_name = 'mine/admin/raw_text.html'


class AdminInitialView(BaseAdminView, TemplateView):
    template_name = 'mine/admin/initial.html'


class AdminMinerListView(BaseAdminView, ListView):
    template_name = 'mine/admin/miners.html'
    queryset = User.objects.filter(Q(is_superuser=True) | Q(groups__name='miner')).order_by('id')


class AdminModeratorListView(BaseAdminView, ListView):
    template_name = 'mine/admin/moderators.html'
    queryset = User.objects.filter(Q(is_superuser=True) | Q(groups__name='moderator')).order_by('id')


class AdminUserActivateView(BaseAdminView, RedirectView):
    url = reverse_lazy('mine:admin-initial')

    def get(self, request, *args, **kwargs):
        users = User.objects.filter(pk=kwargs['pk'])
        if users.exists():
            user = users.first()
            user.is_active = not user.is_active
            user.save()
            miner_url = reverse_lazy('mine:admin-miners')
            moderator_url = reverse_lazy('mine:admin-moderators')
            self.url = miner_url if user.groups.filter(name='miner').exists() else moderator_url
        return super().get(request, *args, **kwargs)


class AdminModerateTextView(BaseAdminView, BaseTextModerationView):
    template_name = 'mine/admin/text_moderate.html'
    success_url = reverse_lazy('mine:admin-moderated-text')


class AdminModeratedTextListView(BaseAdminView, ListView):
    template_name = 'mine/admin/moderated_texts.html'
    queryset = ModeratedText.objects.all()


class AdminModeratedTextDetailView(BaseAdminView, DetailView):
    template_name = 'mine/admin/moderated_text.html'
    queryset = ModeratedText.objects.all()


class AdminProfileView(BaseAdminView, UpdateView):
    form_class = ProfileForm
    template_name = 'mine/admin/profile.html'
    success_url = reverse_lazy('mine:admin-profile')

    def get_object(self, queryset=None):
        return self.request.user


# Moderator views
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
    queryset = Classroom.objects.all()

    def get_queryset(self):
        return self.queryset.filter(owner=self.request.user)

    # def get_context_data(self, **kwargs):
    #     context = super(ModeratorClassroomListView, self).get_context_data(**kwargs)
    #     context['people'] = ClassroomPeople.objects.filter(classroom__in = self.queryset)
    #     print("CONTEXT", ClassroomPeople.objects.filter(classroom__in = self.get_queryset()))
    #     print("QUERYSET", self.get_queryset())
    #     return context


class ModeratorClassroomDetailView(BaseModeratorView, DetailView):
    template_name = "mine/moderator/classroom.html"
    queryset = Classroom.objects.all()


# Miner views
class BaseMinerView(BaseGroupRequiredMixin):
    group_required = 'miner'


class MinerInitialView(BaseMinerView):
    #template_name = 'mine/miner/initial.html'
    template_name = 'mine/miner/tasks.html'
    paginate_by = 9

class MinerInitialViewBeginner(MinerInitialView, ListView):
    queryset = Task.objects.filter(task_level="BEGINNER")

class MinerInitialViewIntermediate(MinerInitialView, ListView):
    queryset = Task.objects.filter(task_level="INTERMEDIATE")

class MinerInitialViewAdvanced(MinerInitialView, ListView):
    queryset = Task.objects.filter(task_level="ADVANCED")


class MinerTaskDetailView(BaseMinerView, BaseTextCreateView, DetailView):
    template_name = 'mine/miner/raw_text_create.html'
    queryset = Task.objects.all()

    def get_success_url(self, **kwargs):
        #Костыль, нужно будет потом переделать...
        obj = Task.objects.get(pk=self.kwargs['pk']).task_level
        success_url = ''
        if obj == 'BEGINNER':
            success_url = reverse_lazy('mine:miner-tasks-beginner')
        elif obj == 'INTERMEDIATE':
            success_url = reverse_lazy('mine:miner-tasks-intermediate')
        elif obj == 'ADVANCED':
            success_url = reverse_lazy('mine:miner-tasks-advanced')
        return success_url

class MinerRawTextListView(BaseMinerView, ListView):
    template_name = 'mine/miner/raw_texts.html'
    queryset = Text.objects.all()


class MinerRawTextCreateView(BaseMinerView, BaseTextCreateView):
    template_name = 'mine/miner/raw_text_create.html'
    success_url = reverse_lazy('mine:miner-raw-texts')


class MinerRawTextDetailView(BaseMinerView, DetailView):
    queryset = Text.objects.all()
    template_name = 'mine/miner/raw_text.html'


class MinerProfileView(BaseMinerView, UpdateView):
    form_class = ProfileForm
    template_name = 'mine/miner/profile.html'
    success_url = reverse_lazy('mine:miner-profile')

    def get_object(self, queryset=None):
        return self.request.user


def initial(request):
    if request.user.is_authenticated:
        if request.user.groups.filter(name='miner').exists():
            return redirect('mine:miner-initial')
        else:
            return redirect('mine:moderator-initial')
    return render(request, 'authentication/initial.html')