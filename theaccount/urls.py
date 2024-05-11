from django.urls import path
from . import views

urlpatterns = [
    path('register/',views.register,name='register'),
    path('login/', views.login, name='login'),
    path('userinfo/',views.current_user,name='user_info'),
    path('profile/',views.user_profile,name='profile'),
    path('all_users_profile/',views.all_users_profile,name='all_users_profile'),
    path('contact_us/',views.contact_us,name='contact_us'),
##
    path('', views.home),
    path('logout/', views.logout_view),
    
]
