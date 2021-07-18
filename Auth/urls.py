from django.urls import path
from . import views

urlpatterns = [
    path('', views.BaseAPI, name='base'),
    path('users', views.UsersList, name="users-list"),
    path('user/<str:pk>', views.UserDetail, name="user-detail"),
    path('profile', views.UserProfile),
    path('login', views.UserLogin, name="user-login"),
    path('register', views.UserCreate, name="user-create"),
]
