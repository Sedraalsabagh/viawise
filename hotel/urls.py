from django.urls import path ,include
from . import views 
from rest_framework import routers
from rest_framework.routers import DefaultRouter

urlpatterns = [  
     path('hotel/<int:star_rating>/',views.hotel, name='hotel_by_rating'),
     path('hotel/',views.hotel_list,name='hotel_list')
         ]