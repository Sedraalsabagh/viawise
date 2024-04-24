from django.urls import path,include
from . import views
from .views import FlightListView,SeedDatabaseAPIView


urlpatterns = [
    path('flight/',views.get_all_flights,name='flight'),
    path('flight/<str:pk>/',views.get_by_id_flights, name='get_by_id_flights'),
    path('<str:pk>/reviews',views.create_review,name='create_review'),
    path('<str:pk>/reviews/delete',views.delete_review,name='delete_review'),
    #path('new/',views.new_flight,name='new_flight'),
    path('search/', views. get_all, name='search-flights'),
    path('seed-database/', SeedDatabaseAPIView.as_view(), name='seed-database'),

    ]