from django.urls import path
from . import views
from .views import ProfileUpdateView, user_login, user_logout, register

urlpatterns = [
    path('register/', register, name='register'),
    path('confirm/<int:user_id>/', views.confirm_email, name='confirm_email'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('profile/edit/', ProfileUpdateView.as_view(), name='profile-edit'),
]