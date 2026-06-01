from django.urls import path
from . import views

print('projects.urls')

app_name = 'projects'

urlpatterns = [
    path('list/', views.ProjectListView.as_view(), name='list'),
    path('<int:pk>/', views.ProjectDetailView.as_view(), name='detail'),
    path('create/', views.ProjectCreateView.as_view(), name='create'),
    path('<int:pk>/edit/', views.ProjectUpdateView.as_view(), name='edit'),
    path('favorites/', views.FavoriteProjectsView.as_view(), name='favorites'),
]
