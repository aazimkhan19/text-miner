from braces.views import SuperuserRequiredMixin
from django.db.models import Q
from django.http import Http404

from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView, ListView, DetailView, RedirectView, UpdateView

from apps.authentication.forms import ProfileForm
from apps.authentication.models import User
from apps.mine.forms import TextForm, ModerateTextForm, CreateTaskForm, CreateClassroomForm, JoinClassroomForm
from apps.mine.models import Text, ModeratedText, Task, Classroom

class BaseTextCreateView(CreateView):
    form_class = TextForm

    def form_valid(self, form):
        """If the form is valid, save the associated model."""
        self.object = form.save()
        self.object.creator = self.request.user
        self.object.task = Task.objects.get(pk=self.kwargs['tpk'])
        self.object.classroom = Classroom.objects.get(pk=self.kwargs['cpk'])
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