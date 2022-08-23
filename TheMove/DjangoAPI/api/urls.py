from django.urls import path
from . import views

urlpatterns = [
    path('', views.GetRoutes),
    path('votes/', views.GetVotes),
    path('users/<str:userString>/', views.GetUser),
    path('users/update/<str:userString>/', views.UpdateVote),
    path('users/create_user', views.CreateNewUser),
    path('users/authenticate', views.AuthenticateUser),
]