from django.urls import path

from apps.authentication.views import RegistrationView, SignInView, ExitView
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy

app_name = 'authentication'
urlpatterns = [
    path('signup/', RegistrationView.as_view(), name='signup'),
    # TODO activate by email stuff
    path('signin/', SignInView.as_view(), name='signin'),
    path('signout/', ExitView.as_view(), name='signout'),
    path('password_reset/', auth_views.PasswordResetView.as_view(
                    success_url=reverse_lazy('authentication:password_reset_done')), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
                    template_name='registration/done_password_reset.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
                    success_url=reverse_lazy('authentication:password_reset_complete')), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]