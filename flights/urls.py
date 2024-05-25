from django.urls import path,include
from . import views
from .views import FlightListView,SeedDatabaseAPIView
#from .exploer import explore_destination



urlpatterns = [
    path('flight/',views.get_all_flights,name='flight'),
    path('flight/<str:pk>/',views.get_by_id_flights, name='get_by_id_flights'),
    path('<str:pk>/reviews',views.create_review,name='create_review'),
    path('<str:pk>/reviews/delete',views.delete_review,name='delete_review'),
    path('seed-database/', SeedDatabaseAPIView.as_view(), name='seed-database'),
    path('all_users_reviews/',views.all_users_reviews,name='all_users_reviews'),
    path('offers/', views.flights_with_offers, name='offer'),
    path('flight_details/<int:flight_id>/', views.flight_details, name='flight_details'),
    path('search1/',views.get_all,name='on_way'),
    path('search2/',views.get_all2,name='Rund Trip'),
    path('flights/',views.get_all_flights,name='flight'),
    path('get_recommendations/', views.get_recommendations, name='get_recommendations'),
    path('get_recommendations2/', views.get_recommendations2, name='get_recommendations2'),
    path('recommendations_user/', views.recommendations_user, name='recommendations_user'),
   # path('explore/',explore_destination, name='explore_destination'),
    path('similar_flights/<int:booking_id>/', views.similar_flights, name='similar_flights'),
    path('recommendations_combined/', views.recommendations_combined, name='recommendations_combined'),


    
             ]




    