from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

print('base.urls')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('api.urls'), name='api'),
    path('',
         RedirectView.as_view(url='/projects/list/', permanent=False),
         name='base'),
    path('users/', include('users.urls'), name='users'),
    path('projects/', include('projects.urls'), name='projects')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
