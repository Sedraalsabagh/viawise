from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserBookingsAPIView,AllBookingsAPIView
from . import views

urlpatterns = [
path('all_booking/', views.all_booking, name='all_booking'),    
path('make_booking/', views.make_booking, name='create_booking'),
path('modify_booking/<int:booking_id>/', views.modify_booking, name='modify_booking'),
path('cancel_booking/', views.cancel_booking, name='cancel_booking'),
path('user-bookings/', UserBookingsAPIView.as_view(), name='user-bookings'),
path('make_payment/', views.make_payment, name='make_payment'),
path('My-booking/', UserBookingsAPIView.as_view(), name='user-bookings'),
#path('send_notification/', views.send_notification, name='send_notification'),
path('load_seed_data/', views.load_seed_data, name='load_seed_data'),
path('AllBookings/', AllBookingsAPIView.as_view(), name='AllBookings'),
path('booking/', views.booking, name='create_booking'),
path('privat_offers/', views.get_user_point_balance, name='privatoffers'),
path('booking_details/<int:id_booking>', views.booking_details),
path('tickets/<int:booking_id>', views.get_Tickets),



    
]
