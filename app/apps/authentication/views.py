from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.http.response import HttpResponseRedirect
from django.views.generic import CreateView
from django.contrib.auth import login
from config.settings.common import AUTHENTICATION_BACKENDS

from apps.authentication.forms import UserCreationForm, UserAuthForm


class RegistrationView(CreateView):
    form_class = UserCreationForm
    template_name = 'authentication/registration.html'
    success_url = reverse_lazy('initial')

    def form_valid(self, form):
        self.object = form.save()
        login(self.request, self.object, backend=AUTHENTICATION_BACKENDS[1])
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        return super(RegistrationView, self).form_invalid(form)


class SignInView(LoginView):
    template_name = 'authentication/signin.html'
    form_class = UserAuthForm

    def get_success_url(self):
        return reverse_lazy('initial')


class ExitView(LogoutView):
    def get_next_page(self):
        return reverse_lazy('initial')
