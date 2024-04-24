from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserBookingsAPIView
from . import views

urlpatterns = [
#path('bookings/', BookingView.as_view(), name='create_booking'),
#path('bookings/', views.Bookingview, name='create_booking'),
path('bookings/', views.create_booking, name='create_booking'),
path('user-bookings/', UserBookingsAPIView.as_view(), name='user-bookings'),
path('make_payment/', views.make_payment, name='make_payment'),
path('user-booking/', UserBookingsAPIView.as_view(), name='user-bookings'),
#path('send_notification/', views.send_notification, name='send_notification'),
path('load_seed_data/', views.load_seed_data, name='load_seed_data'),

]
