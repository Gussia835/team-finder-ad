from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('api.urls'), name='api'),
    path('users/', include('users.urls'), name='users'),
    path('projects/', include('projects.urls'), name='projects'),
    path('',
         RedirectView.as_view(url='/projects/list/', permanent=False)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
