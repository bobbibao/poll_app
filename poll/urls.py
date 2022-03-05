from telnetlib import LOGOUT
from django.urls import path, include
from .views import Login, Logout, poll_detail, register, poll,search, index, view, profile, vote,end, result, back, edit, add, delete, add_choice
urlpatterns = [
    path('login/', Login.as_view(), name = "login"),
    path('logout/', Logout.as_view(), name = "logout"),
    path('register/', register, name = "register"),
    path('poll/', poll, name = "poll"),
    path('search/', search, name="search"),
    path('', index, name="index"),
    path('view/', view, name="view"),
    path('<int:poll_id>/', poll_detail, name="detail"),
    path('<int:poll_id>/vote', vote, name="vote"),
    path('result/<int:poll_id>/', result.as_view(), name="resutl"),
    path('end/<int:poll_id>/', end, name="end"),
    path('back/<int:poll_id>/', back, name="back"),
    path('edit/<int:poll_id>/', edit, name="edit"),
    path('delete/<int:poll_id>/', delete, name="delete"),
    path('edit/<int:poll_id>/choice/add/', add_choice, name='add_choice'),
    path('add/<int:poll_id>/', add, name="add"),
    path('<str:username>/', profile.as_view(), name="profile"),
]