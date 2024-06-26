from django.shortcuts import render
from django.shortcuts import render,get_object_or_404 
from rest_framework.decorators import api_view ,permission_classes
from rest_framework.response import Response
from .models import Flight,Airline,SeatType,Review
from rest_framework.pagination import PageNumberPagination
from django.db.models import Avg
from .serializer import FlightSerializer,SeatSerializer,ReviewSerializer,OfferSerializer,FlightProfileSerializer
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
from firebase_admin import messaging
import firebase_admin
from firebase_admin import credentials
from django.db.models import Prefetch
from dotenv import load_dotenv
import os


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
   serializer=FlightProfileSerializer(filterset.qs ,many=True)
   return Response({"flights":serializer.data})


@api_view(['GET'])  
def get_all2(request) :
   filterset=FlightsFilter2(request.GET,queryset=Flight.objects.all().order_by('id')) 
   serializer=FlightProfileSerializer(filterset.qs ,many=True)
   return Response({"flights":serializer.data})

@api_view(['GET'])  
def get_all2(request):
    filterset = FlightsFilter2(request.GET, queryset=Flight.objects.all().order_by('id')) 
    return Response({"flights": filterset.qs})



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
    current_datetime = timezone.now()  #خزنت الوقت الحالي  

    
    flights = Flight.objects.prefetch_related(  # منشان ORM 
        Prefetch('offer_set', queryset=Offer.objects.filter(
            start_date__lte=current_datetime.date(),
            end_date__gte=current_datetime.date()
        ))
    ).filter(offer__isnull=False).distinct().order_by('-offer__discount_percentage') # distinct يعني فريدة

    flights_data = []
    for flight in flights:
        flight_data = FlightSerializer(flight).data
        offers_data = []

        for offer in flight.offer_set.all():
            offer_start_datetime = timezone.make_aware(datetime.combine(offer.start_date, time.min)) # الكومبين منشان يندمج الوقت مع التاريج 
            offer_end_datetime = timezone.make_aware(datetime.combine(offer.end_date, time.max)) 

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
            
 

load_dotenv()
admin_sdk_path  =os.getenv('ADMIN_SDK_PATH')
cred = credentials.Certificate(admin_sdk_path)
firebase_admin.initialize_app(cred)

def send_push_notification(token, title, body):
    message = messaging.Message(
        notification=messaging.Notification(title=title, body=body),
        token=token,
    )
    
    try:
        response = messaging.send(message)
        return {'status': 'success', 'response': response}
    except Exception as e:
        return {'status': 'error', 'error': str(e)}                

    return Response(flights_data)

result = send_push_notification("ftmGf_xeSS23JuN0AKGcTB:APA91bFGPgf00v4BgXFj41qqJz60Qp6p_1NK0qRCnfIyY55JIWc0h-C0dLu5HmEr1INvHEcBqi3ELhCNgD6nktB9Xso07gk0a3uNUSR4ewNcm6IvOAmq6wS0Nz0pV99gUBgnebEgT_Vr", 'HI', 'this is offers')
print(result)


'''

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

                
                if offer_start_datetime == current_datetime:
                    
                    tokens = User.objects.filter(is_active=True).values_list('fcm_token', flat=True)
                    
                    for token in tokens:
                        send_push_notification(token, 'Hello all', f": {offer.title}")

        if offers_data:
            flight_data['offers'] = offers_data
            flights_data.append(flight_data)

    return Response(flights_data)
'''




@api_view(['GET'])
def flights_offers(request):
    
    flights_with_offers = Flight.objects.filter(offer__isnull=False).distinct().order_by('-offer__discount_percentage')
    
   
    serializer = FlightSerializer(flights_with_offers, many=True)
    
    
    return Response(serializer.data)



@api_view(['GET'])
def flight_details1(request, flight_id):
    try:
        flight = Flight.objects.get(id=flight_id)
    except Flight.DoesNotExist:
        return Response(status=404)

    serializer = FlightProfileSerializer(flight)
    return Response(serializer.data)

'''
@api_view(['GET'])
def flight_details(request, flight_id1, flight_id2):
    try:
        flight1 = Flight.objects.get(id=flight_id1)
        flight2 = Flight.objects.get(id=flight_id2)
    except Flight.DoesNotExist:
        return Response(status=404)

    serializer1 = FlightProfileSerializer(flight1)
    serializer2 = FlightProfileSerializer(flight2)
    return Response({"flight1": serializer1.data, "flight2": serializer2.data})
'''
@api_view(['GET'])
def flight_details(request, flight_id1, flight_id2):
    try:
        flight1 = Flight.objects.get(id=flight_id1)
        flight2 = Flight.objects.get(id=flight_id2)
    except Flight.DoesNotExist:
        return Response(status=404)

    
    data = {
        "outbound_flight_id": flight1.id,
        "notes_outbound": flight1.notes,
        "ratings_outbound": flight1.ratings,
        "departure_date_outbound": flight1.departure_date,
        "airportDeparture_outbound": flight1.airportDeparture,
        "airportArrival_outbound": flight1.airportArrival,
        "departure_city_outbound": flight1.departure_city,
        "destination_city_outbound": flight1.destination_city,
        "departure_country_outbound": flight1.departure_country,
        "destination_country_outbound": flight1.destination_country,
        "price_flight_outbound": float(flight1.price_flight),
        "return_id": flight2.id,
        "notes_return": flight2.notes,
        "ratings_return": flight2.ratings,
        "departure_date_return": flight2.departure_date,
        "airportDeparture_return": flight2.airportDeparture,
        "airportArrival_return": flight2.airportArrival,
        "departure_city_return": flight2.departure_city,
        "destination_city_return": flight2.destination_city,
        "departure_country_return": flight2.departure_country,
        "destination_country_return": flight2.destination_country,
        "price_flight_return": float(flight2.price_flight)
    }

    return Response(data)



@api_view(['GET']) # عملتيها منشان العروض
def similar_flights(request, booking_id):
    try:
        booking = Booking.objects.get(pk=booking_id)
    except Booking.DoesNotExist:
        return Response({'error': 'Booking not found'}, status=404)

    outbound_flight = booking.outbound_flight
    if not outbound_flight:
        return Response({'error': 'No outbound flight found for this booking'}, status=404)

    
    similar_flights = Flight.objects.filter(
        airportDeparture=outbound_flight.airportDeparture,
        airportArrival=outbound_flight.airportArrival
    ).exclude(id=outbound_flight.id).order_by('departure_date') #هيك بتروح الرحلة نفسها 

    serializer = FlightProfileSerializer(similar_flights, many=True)
    return Response(serializer.data)
#






























from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.http import JsonResponse
from sklearn.metrics.pairwise import cosine_similarity
from theaccount.models import UserProfile
from .models import Review, Flight
from rest_framework.permissions import IsAuthenticated
from sklearn.preprocessing import LabelEncoder
import numpy as np
import pandas as pd
from booking.models import Booking
from datetime import datetime, date

def jaccard_distance_weighted(u, v, weights=None):
    if weights is None:
        weights = np.ones(len(u))
    intersection = np.minimum(u, v)
    union = np.maximum(u, v)
    return 1.0 - (np.dot(weights, intersection) / np.dot(weights, union))

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def combined_recommendations(request):
    user = request.user
    data = request.data

    recommendations = {
        "recommendations1": get_recommendations1(user, data),
        "recommendations2": get_recommendations2(user, data),
        "recommendations3": recommendations_user(user)
    }

    return JsonResponse(recommendations)

def get_recommendations1(user, data):


    user_current_city = data.get('current_city', '').capitalize().strip()  
    price_preference = float(data.get('budget', 0))
    activity_preference = data.get('preferred_activity', '').capitalize().strip()
    climate_preference = data.get('preferred_climate', '').capitalize().strip()
    type_preference = data.get('travel_goal', '').capitalize().strip()


    flights = Flight.objects.filter(departure_city__iexact=user_current_city).values('id', 'price_flight', 'departure_city', 'destination_city', 'destination_activity', 'destination_climate', 'destination_type', 'departure_date')
    flights_df = pd.DataFrame(flights)
    flights_df['price_flight'] = flights_df['price_flight'].astype(float)


    flights_df['departure_date'] = pd.to_datetime(flights_df['departure_date'])


    current_time = datetime.now()
    flights_df = flights_df[flights_df['departure_date'] >= current_time]


    flights_df['departure_city'] = flights_df['departure_city'].str.capitalize()
    flights_df['destination_activity'] = flights_df['destination_activity'].str.capitalize()
    flights_df['destination_climate'] = flights_df['destination_climate'].str.capitalize()
    flights_df['destination_type'] = flights_df['destination_type'].str.capitalize()


    features = ['price_flight', 'destination_activity', 'destination_climate', 'destination_type']
    weights = {
        'price_flight': 3,
        'destination_activity': 2,
        'destination_climate': 3,
        'destination_type': 2
    }


    flights_features_encoded = pd.get_dummies(flights_df[features])
    flights_features_array = flights_features_encoded.values

    # Adjust weights to match the number of features
    weights_array = np.ones(flights_features_array.shape[1])

    # Calculate similarity matrix
    similarity_matrix = np.zeros((len(flights_features_array), len(flights_features_array)))
    for i in range(len(flights_features_array)):
        for j in range(i, len(flights_features_array)):
            similarity_matrix[i, j] = jaccard_distance_weighted(flights_features_array[i], flights_features_array[j], weights_array)
            similarity_matrix[j, i] = similarity_matrix[i, j]


    user_preferences = pd.DataFrame({
        'price_flight': [price_preference],
        'destination_activity_' + activity_preference.lower(): [1],
        'destination_climate_' + climate_preference.lower(): [1],
        'destination_type_' + type_preference.lower(): [1]
    })
    merged_data = pd.concat([flights_features_encoded, user_preferences], ignore_index=True).fillna(0)
    user_similarity = cosine_similarity(merged_data)[-1][:-1]


    top_similar_flights_indices = user_similarity.argsort()[::-1][:4]


    recommended_flights = []
    for idx in top_similar_flights_indices:
        flight_data = flights_df.iloc[idx].to_dict()
        flight_data['destination_city'] = flights_df.iloc[idx]['destination_city']
        flight_data['departure_date'] = flights_df.iloc[idx]['departure_date'].isoformat()
        recommended_flights.append(flight_data)

    return recommended_flights

def get_recommendations2(user, data):
    # Implementation of the second recommendation logic
    bookings = Booking.objects.filter(user=user, outbound_flight__isnull=False).values('outbound_flight')
    outbound_flights = [booking['outbound_flight'] for booking in bookings]

    flights = Flight.objects.all().values('id', 'price_flight', 'departure_city', 'destination_activity', 'destination_climate', 'destination_type', 'departure_date')
    flights_df = pd.DataFrame(flights)
    flights_df['price_flight'] = flights_df['price_flight'].astype(float)

    flights_df['departure_city'] = flights_df['departure_city'].str.capitalize()
    flights_df['destination_activity'] = flights_df['destination_activity'].str.capitalize()
    flights_df['destination_climate'] = flights_df['destination_climate'].str.capitalize()
    flights_df['destination_type'] = flights_df['destination_type'].str.capitalize()

    features = ['price_flight', 'destination_activity', 'destination_climate', 'destination_type', 'departure_city']
    flights_features_encoded = pd.get_dummies(flights_df[features])

    all_columns = flights_features_encoded.columns
    flights_features_array = flights_features_encoded.values

    similarity_matrix = np.zeros((len(flights_features_array), len(flights_features_array)))
    current_time = datetime.now()

    for i in range(len(flights_features_array)):
        for j in range(i, len(flights_features_array)):
            flight1_departure_date = flights_df.iloc[i]['departure_date']
            flight2_departure_date = flights_df.iloc[j]['departure_date']

            if isinstance(flight1_departure_date, date):
                flight1_departure_date = flight1_departure_date.strftime("%Y-%m-%d")
            if isinstance(flight2_departure_date, date):
                flight2_departure_date = flight2_departure_date.strftime("%Y-%m-%d")

            flight1_departure_date = datetime.strptime(flight1_departure_date, "%Y-%m-%d")
            flight2_departure_date = datetime.strptime(flight2_departure_date, "%Y-%m-%d")

            if flight1_departure_date >= current_time and flight2_departure_date >= current_time:
                similarity_matrix[i, j] = jaccard_distance_weighted(flights_features_array[i], flights_features_array[j])
                similarity_matrix[j, i] = similarity_matrix[i, j]
            else:
                similarity_matrix[i, j] = 0
                similarity_matrix[j, i] = 0

    user_similarity = np.zeros(len(flights_features_array))
    for flight_id in outbound_flights:
        user_preferences = Flight.objects.filter(id=flight_id).values('price_flight', 'departure_city', 'destination_activity', 'destination_climate', 'destination_type')[0]
        user_preferences_df = pd.DataFrame([user_preferences])
        user_preferences_encoded = pd.get_dummies(user_preferences_df).reindex(columns=all_columns, fill_value=0).values[0]
        for i, flight_features in enumerate(flights_features_array):
            user_similarity[i] += 1 - jaccard_distance_weighted(user_preferences_encoded, flight_features)

    top_similar_flights_indices = user_similarity.argsort()[::-1][:5]

    recommended_flights = []
    for idx in top_similar_flights_indices:
        recommended_flights.append(flights_df.iloc[idx].to_dict())

    return recommended_flights

def recommendations_user(user):
    # Implementation of the third recommendation logic
    user_id = user.id
    if user_id is not None:
        users_data = UserProfile.objects.all().values()
        reviews_data = Review.objects.all().values()

        if not users_data or not reviews_data:
            return []

        users_df = pd.DataFrame(users_data)
        reviews_df = pd.DataFrame(reviews_data)

        users_df.rename(columns={'user_id': 'user'}, inplace=True)
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

        weights = [1, 0.1, 2, 1, 3]
        user_variables = ['age', 'gender_encoded', 'occupation_encoded', 'marital_status_encoded', 'address_encoded']
        users_similarity_matrix_jaccard = np.zeros((len(users_df), len(users_df)))

        for i, user1 in enumerate(users_df[user_variables].values):
            for j, user2 in enumerate(users_df[user_variables].values):
                intersection = np.sum(np.minimum(user1, user2) * weights)
                union = np.sum(np.maximum(user1, user2) * weights)
                similarity = intersection / union if union != 0 else 0
                users_similarity_matrix_jaccard[i, j] = similarity

        user_index = users_df[users_df['user'] == user_id].index[0]
        similar_users_indices = np.where(users_similarity_matrix_jaccard[user_index] > 0.5)[0]

        if len(similar_users_indices) == 0:
            return []

        recommended_flights = []

        for similar_user_idx in similar_users_indices:
            similar_user_profile = users_df.iloc[similar_user_idx]
            similar_user_reviews = reviews_df[reviews_df['user_id'] == similar_user_profile['user']]

            if 'flight_id' in similar_user_reviews.columns:
                similar_user_reviews = similar_user_reviews.dropna(subset=['flight_id'])
                recommended_flights.extend(similar_user_reviews[similar_user_reviews['ratings'] >= 3]['flight_id'].dropna().tolist())

        if len(recommended_flights) == 0:
            return []

        recommended_flights_details = Flight.objects.filter(id__in=recommended_flights).values()

        return list(recommended_flights_details)
    else:
        return []

