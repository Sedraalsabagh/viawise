from django.urls import path,include
from . import views
from .views import FlightListView,SeedDatabaseAPIView


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
    path('recommendations1/', views.get_recommendations_user, name='get_recommendations_user'),
    path('get_recommendations/', views.get_recommendations, name='get_recommendations'),
    #path('recommend-flights/', RecommendFlightsAPIView.as_view(), name='recommend-flights'),
    #path('recommendations/', get_recommendations, name='get_recommendations'),


    
             ]




    