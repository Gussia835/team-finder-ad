from django.urls import path
from . import views

print('users.urls')

app_name = 'users'

urlpatterns = [
    path('register/',
         views.register_view,
         name='register'),
    path('login/',
         views.login_view,
         name='login'),
    path('logout/',
         views.logout_view,
         name='logout'),
    path('list/',
         views.UserListView.as_view(),
         name='user_list'),
    path('<int:pk>/',
         views.UserDetailView.as_view(),
         name='user_detail'),
]
