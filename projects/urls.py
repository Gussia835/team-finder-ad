from django.urls import path

from . import views

app_name = 'projects'

urlpatterns = [
    path('list/', views.ProjectListView.as_view(), name='list'),
    path('favorites/', views.FavoriteProjectsView.as_view(), name='favorites'),
    path(
        'create-project/',
        views.ProjectCreateView.as_view(),
        name='create',
    ),
    path('skills/', views.skills_autocomplete, name='skills_autocomplete'),
    path(
        '<int:pk>/complete/',
        views.complete_project_view,
        name='complete',
    ),
    path(
        '<int:pk>/toggle-favorite/',
        views.toggle_favorite_view,
        name='toggle_favorite',
    ),
    path(
        '<int:pk>/toggle-participate/',
        views.toggle_participate_view,
        name='toggle_participate',
    ),
    path(
        '<int:pk>/skills/add/',
        views.add_project_skill_view,
        name='add_skill',
    ),
    path(
        '<int:pk>/skills/<int:skill_id>/remove/',
        views.remove_project_skill_view,
        name='remove_skill',
    ),
    path('<int:pk>/edit/', views.ProjectUpdateView.as_view(), name='edit'),
    path('<int:pk>/', views.ProjectDetailView.as_view(), name='detail'),
]
