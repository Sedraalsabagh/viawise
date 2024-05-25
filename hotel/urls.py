from django.urls import path ,include
from . import views 
from rest_framework import routers
from rest_framework.routers import DefaultRouter

urlpatterns = [  
     path('hotel/<int:star_rating>/',views.hotel, name='hotel_by_rating'),
     path('hotel/',views.hotel_list,name='hotel_list') ,
     path('hotelfilter/',views.hotels_filter,name='hotels_filter'),
     path('hotel_details/',views.hotel_details,name='hotel_details')

         ]

         
         
         
         