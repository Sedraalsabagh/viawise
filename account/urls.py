from django.urls import path
from . import views

urlpatterns = [
    path('register/',views.register,name='register'),
    path('login/', views.login, name='login'),
    path('userinfo/',views.current_user,name='user_info'),
    path('profile/',views.user_profile,name='profile'),

]
