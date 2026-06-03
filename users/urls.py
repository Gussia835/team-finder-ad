from django.urls import path

from . import views

app_name = 'users'

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('list/', views.UserListView.as_view(), name='user_list'),
    path('skills/', views.skills_autocomplete, name='skills_autocomplete'),
    path('edit-profile/', views.edit_profile_view, name='edit_profile'),
    path('change-password/', views.change_password_view, name='change_password'),
    path(
        '<int:pk>/skills/add/',
        views.add_user_skill,
        name='add_skill',
    ),
    path(
        '<int:pk>/skills/<int:skill_id>/remove/',
        views.remove_user_skill,
        name='remove_skill',
    ),
    path('<int:pk>/', views.UserDetailView.as_view(), name='user_detail'),
]
