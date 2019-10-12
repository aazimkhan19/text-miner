"""unilever URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from apps.mine.view import initial as mine_view

patterns = [
    path('', mine_view.initial, name='initial'),
    path('authentication/', include('apps.authentication.urls')),
    path('mine/', include('apps.mine.urls')),
    path('social/', include('social_django.urls', namespace='social')),
]

if settings.DEBUG:
    import debug_toolbar
    patterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + patterns


urlpatterns = [
    path('', include(patterns)),
    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
