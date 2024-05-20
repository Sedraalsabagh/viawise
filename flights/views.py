from django.shortcuts import render
from django.shortcuts import render,get_object_or_404 
from rest_framework.decorators import api_view ,permission_classes
from rest_framework.response import Response
from .models import Flight,Airline,SeatType,Review
from rest_framework.pagination import PageNumberPagination
from django.db.models import Avg
from .serializer import FlightSerializer,SeatSerializer,ReviewSerializer,OfferSerializer
from .filters import FlightsFilter
from .filters import *
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import AccessToken
from .filters import FlightsFilter
from rest_framework import generics
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework import status
from django.core.management import call_command
from .models import Offer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.utils import timezone
from datetime import datetime,time
from django.utils.timezone import make_aware
from .serializer import FlightProfileSerializer

# Create your views here.
@api_view(['GET'])
def get_all_flights(request) :
    flights=Flight.objects.all()
    serializer=FlightProfileSerializer(flights,many=True)
    return Response({"flights":serializer.data}) 


###################################
@api_view(['GET'])
def get_all_flights(request) :
    flights=Flight.objects.all()
    serializer=FlightSerializer(flights,many=True)
    return Response({"flights":serializer.data}) 
#####################################################



@api_view(['POST'])
def get_by_id_flights(request,pk) :
    flights = get_object_or_404(Flight, id=pk)
    serializer=FlightSerializer(flights,many=False)
    print(flights)
    return Response({"flights":serializer.data})   


@api_view(['GET'])  
def get_all(request) :
   filterset=FlightsFilter(request.GET,queryset=Flight.objects.all().order_by('id')) #غيرتي من Flight to FlightSeatType
   serializer=FlightSerializer(filterset.qs ,many=True)
   return Response({"flights":serializer.data})


@api_view(['GET'])  
def get_all2(request) :
   filterset=FlightsFilter2(request.GET,queryset=Flight.objects.all().order_by('id')) #غيرتي من Flight to FlightSeatType
   serializer=FlightSerializer(filterset.qs ,many=True)
   return Response({"flights":serializer.data})

@api_view(['GET'])
def get_round_trip_flights(request):
    filterset = RoundTripFilter(request.GET, queryset=Flight.objects.all().order_by('id'))
    if filterset.is_valid():
        serializer = FlightSerializer(filterset.qs, many=True)
        return Response({"flights": serializer.data})
    else:
        return Response({"error": "Invalid parameters"}, status=400)


class SeedDatabaseAPIView(APIView):
    def get(self, request, format=None):
        try:
            call_command('seed')

            return Response({"message": "Database seeding successful."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

'''
@api_view(['POST'])
@permission_classes([IsAuthenticated]) # بس الموظف يلي عامل ريجستر بيقدر يضيف رحلات
def new_flight(request) :
    data=request.data
    serializer=FlightSerializer(data=data)
    
    if serializer.is_valid():
    
       airline_id = data.pop('airline')  # Extract airline ID from request data
       flights=Flight.objects.create(**data,Employee=request.Employee)
       req=FlightSerializer(Flight,many=False)

       return Response({"flights":req.data})   


    else: 
       return   Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

'''


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_review(request, pk):
    user = request.user
    flight = get_object_or_404(Flight, id=pk)
    data = request.data
    review = flight.reviews.filter(user=user)
    
    if data['ratings'] <= 0 or data['ratings'] > 5:
        flight = Flight.objects.create(**data, user=request.user)
        res = FlightSerializer(flight, many=False)
        
        return Response({"error": 'please select between 1 to 5 only'}, status=status.HTTP_400_BAD_REQUEST)
    elif review.exists():
        new_review = {'ratings': data['ratings'], 'comment': data['comment']}
        review.update(**new_review)
        
        rating = flight.reviews.aggregate(avg_ratings=Avg('ratings'))
        flight.ratings = rating['avg_ratings']
        flight.save()
        return Response({'details': 'Flight review updated'})
    else:
        Review.objects.create(
            user=user,
            flight=flight,
            ratings=data['ratings'],
            comment=data['comment']
        )
        rating = flight.reviews.aggregate(avg_ratings=Avg('ratings'))
        flight.ratings = rating['avg_ratings']
        flight.save()
        return Response({'details': 'flight review created'})



@api_view
@permission_classes([IsAuthenticated])
def delete_review(request,pk):
    user=request.user
    flight=get_object_or_404(Flight,id=pk)
    review=flight.reviews.filter(user=user)

    if review.exists():
        review.delete|()
        rating=flight.reviews.aggregate(avg_ratings=Avg('rating'))
        if  rating['avg_ratings'] is None:
         rating['avg_ratings'] =0
         flight.ratings=rating['avg_ratings']
         flight.save()
         return Response({'details':'flight review deleted'})

    else:
        return Response({'error':'Review not found'},status=status.HTTP_404_NOT_FOUND)






@api_view(['GET'])
def all_users_reviews(request):
    if request.method == 'GET':
        user_reviews = Review.objects.all()
        serializer = ReviewSerializer(user_reviews, many=True)
        return Response(serializer.data)


class FlightListView(generics.ListAPIView):
    queryset = Flight.objects.all()
    serializer_class = FlightSerializer
    filterset_class = FlightsFilter




class SeatViewSet(viewsets.ModelViewSet):
    queryset = SeatType.objects.all()
    serializer_class = SeatSerializer



@api_view(['GET'])
def flight_explor(request):
    
    if request.method == 'GET':
        flights = Flight.objects.all().order_by('-ratings')  
        serializer = FlightSerializerexplor(flights, many=True)
        return Response(serializer.data) 
    
@api_view(['GET'])
def flights_with_offers(request):
   
    current_datetime = timezone.now()

    
    flights_with_offers = Flight.objects.filter(offer__isnull=False).distinct().order_by('-offer__discount_percentage')

    
    flights_data = []
    for flight in flights_with_offers:
        flight_data = FlightSerializer(flight).data
        offers_data = []

        for offer in flight.offer_set.all():
            
            offer_start_datetime = make_aware(datetime.combine(offer.start_date, time.min))
            offer_end_datetime = make_aware(datetime.combine(offer.end_date, time.max))

            
            if offer_start_datetime <= current_datetime <= offer_end_datetime:
                offer_data = {
                    'title': offer.title,
                    'discount_percentage': offer.discount_percentage,
                    'start_date': offer.start_date,
                    'end_date': offer.end_date,
                    'description': offer.description,
                    'conditions': offer.conditions,
                }
                offers_data.append(offer_data)

        if offers_data:
            flight_data['offers'] = offers_data
            flights_data.append(flight_data)

    return Response(flights_data)


@api_view(['GET'])
def flights_offers(request):
    
    flights_with_offers = Flight.objects.filter(offer__isnull=False).distinct().order_by('-offer__discount_percentage')
    
   
    serializer = FlightSerializer(flights_with_offers, many=True)
    
    
    return Response(serializer.data)



@api_view(['GET'])
def flight_details(request, flight_id):
    try:
        flight = Flight.objects.get(id=flight_id)
    except Flight.DoesNotExist:
        return Response(status=404)

    serializer = FlightProfileSerializer(flight)
    return Response(serializer.data)
















#Recommendation
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.http import JsonResponse
from theaccount.models import UserProfile
from .models import Review
from rest_framework.permissions import IsAuthenticated
from sklearn.preprocessing import LabelEncoder
import numpy as np
import pandas as pd

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_recommendations_user(request):
    user_id = request.user.id
    if user_id is not None:
        users_data = UserProfile.objects.all().values()
        reviews_data = Review.objects.all().values()

        if not users_data or not reviews_data:
            return JsonResponse({"error": "No sufficient data for recommendations"}, status=400)

        users_df = pd.DataFrame(users_data)
        reviews_df = pd.DataFrame(reviews_data)
        
        if user_id not in users_df['user_id'].values:
            return JsonResponse({"error": "User ID not found in the database"}, status=404)

        users_df.rename(columns={'user': 'user_id'}, inplace=True)
        users_df.fillna(users_df.mode().iloc[0], inplace=True)
        
        gender_mapping = {'male': 0, 'female': 1}
        users_df['gender_encoded'] = users_df['gender'].map(gender_mapping)
        users_df.drop('gender', axis=1, inplace=True)
        
        label_encoder = LabelEncoder()
        users_df['address_encoded'] = label_encoder.fit_transform(users_df['address'])
        users_df.drop('address', axis=1, inplace=True)
        users_df['occupation_encoded'] = label_encoder.fit_transform(users_df['occupation'])
        users_df.drop('occupation', axis=1, inplace=True)
        users_df['marital_status_encoded'] = label_encoder.fit_transform(users_df['marital_status'])
        users_df.drop('marital_status', axis=1, inplace=True)
        
        weights = [1, 0.1, 1, 1, 1]
        user_variables = ['age', 'gender_encoded', 'occupation_encoded', 'marital_status_encoded', 'address_encoded']
        users_similarity_matrix_jaccard = np.zeros((len(users_df), len(users_df)))

        for i, user1 in enumerate(users_df[user_variables].values):
            for j, user2 in enumerate(users_df[user_variables].values):
                intersection = np.sum(np.minimum(user1, user2) * weights)
                union = np.sum(np.maximum(user1, user2) * weights)
                similarity = intersection / union
                users_similarity_matrix_jaccard[i, j] = similarity

        users_similarity_df_jaccard = pd.DataFrame(users_similarity_matrix_jaccard, index=users_df['user_id'], columns=users_df['user_id'])

        similar_users_indices = np.where(users_similarity_df_jaccard.loc[user_id] > 0.7)[0]

        recommended_flights = []

        for similar_user_idx in similar_users_indices:
            similar_user_profile = users_df.iloc[similar_user_idx]
            similar_user_reviews = reviews_df[reviews_df['user_id'] == similar_user_profile['user_id']]
            
            if 'reviews' in similar_user_reviews.columns:
                similar_user_reviews = similar_user_reviews.dropna(subset=['reviews'])
                recommended_flights.extend(similar_user_reviews[similar_user_reviews['ratings'] >= 3]['reviews'].dropna().tolist())

        recommended_flights = list(set(recommended_flights))
        
        return JsonResponse({"recommendations": recommended_flights})
    else:
        return JsonResponse({"error": "User ID is missing"}, status=400)













#Recommendation2
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse
from datetime import datetime, date
from .models import Flight
from booking.models import Booking
import pandas as pd
import numpy as np

def jaccard_distance_weighted(u, v, weights=None):
    if weights is None:
        weights = np.ones(len(u))
    intersection = np.minimum(u, v)
    union = np.maximum(u, v)
    return 1.0 - (np.dot(weights, intersection) / np.dot(weights, union))

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_recommendations(request):
    user = request.user

    # Fetch bookings for the current user
    bookings = Booking.objects.filter(user=user, outbound_flight__isnull=False).values('outbound_flight')

    outbound_flights = [booking['outbound_flight'] for booking in bookings]

    # Fetch flight data
    flights = Flight.objects.all().values('id', 'price_flight', 'departure_city', 'destination_activity', 'destination_climate', 'destination_type', 'departure_date')
    flights_df = pd.DataFrame(flights)
    flights_df['price_flight'] = flights_df['price_flight'].astype(float)

    # Preprocess flight data
    flights_df['departure_city'] = flights_df['departure_city'].str.capitalize()
    flights_df['destination_activity'] = flights_df['destination_activity'].str.capitalize()
    flights_df['destination_climate'] = flights_df['destination_climate'].str.capitalize()
    flights_df['destination_type'] = flights_df['destination_type'].str.capitalize()

    features = ['price_flight', 'destination_activity', 'destination_climate', 'destination_type', 'departure_city']
    weights = np.ones(len(features))

    flights_features_encoded = pd.get_dummies(flights_df[features])
    flights_features_array = flights_features_encoded.values

    similarity_matrix = np.zeros((len(flights_features_array), len(flights_features_array)))
    current_time = datetime.now()

    for i in range(len(flights_features_array)):
        for j in range(i, len(flights_features_array)):
            flight1_departure_date = flights_df.iloc[i]['departure_date']
            flight2_departure_date = flights_df.iloc[j]['departure_date']

            # Verify if the dates are date objects and convert them to strings if necessary
            if isinstance(flight1_departure_date, date):
                flight1_departure_date = flight1_departure_date.strftime("%Y-%m-%d")
            if isinstance(flight2_departure_date, date):
                flight2_departure_date = flight2_departure_date.strftime("%Y-%m-%d")

            flight1_departure_date = datetime.strptime(flight1_departure_date, "%Y-%m-%d")
            flight2_departure_date = datetime.strptime(flight2_departure_date, "%Y-%m-%d")

            if flight1_departure_date >= current_time and flight2_departure_date >= current_time:
                similarity_matrix[i, j] = jaccard_distance_weighted(flights_features_array[i], flights_features_array[j], weights)
                similarity_matrix[j, i] = similarity_matrix[i, j]
            else:
                similarity_matrix[i, j] = 0
                similarity_matrix[j, i] = 0

    user_similarity = np.zeros(len(flights_features_array))
    for flight_id in outbound_flights:
        user_preferences = Flight.objects.filter(id=flight_id).values('price_flight', 'departure_city', 'destination_activity', 'destination_climate', 'destination_type')[0]
        user_preferences_encoded = pd.get_dummies(pd.DataFrame(user_preferences).T).reindex(columns=flights_features_encoded.columns, fill_value=0).values[0]
        for i, flight_features in enumerate(flights_features_array):
            user_similarity[i] += 1 - jaccard_distance_weighted(user_preferences_encoded, flight_features, weights)

    top_similar_flights_indices = user_similarity.argsort()[::-1][:5]

    recommended_flights = []
    for idx in top_similar_flights_indices:
        recommended_flights.append(flights_df.iloc[idx].to_dict())

    return JsonResponse({"recommendations": recommended_flights})
