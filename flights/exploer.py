'''
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated ,AllowAny
from rest_framework.response import Response
from .models import  Flight
from booking.models import *
from .serializer import *
from booking.serializers import *
import pandas as pd
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity




def preprocess_text(text):
    lemm = WordNetLemmatizer()
    
    stop_words = set(stopwords.words('english'))
    
    words = word_tokenize(text.lower()) # لقسم 
    
    filtered_words = [lemm.lemmatize(word) for word in words if word.isalnum() and word not in stop_words]
    
    return ' '.join(filtered_words)

def recommender_by_description(description, data):
    
    description_processed = preprocess_text(description)
    
    data['processed_description'] = data['description'].apply(preprocess_text)
    
    tfidf_vectorizer = TfidfVectorizer() # حولت النص لمتجهات منشان اعرف مهمة كل حرف 
    
    tfidf_matrix = tfidf_vectorizer.fit_transform(data['processed_description'])
    
    description_vector = tfidf_vectorizer.transform([description_processed])
    
    cos_similarities = cosine_similarity(description_vector, tfidf_matrix).flatten()
    
    data['similarity'] = cos_similarities
    
    data = data.sort_values(by=['similarity', 'ratings'], ascending=[False, False])
    
    data.reset_index(drop=True, inplace=True)
    
    return data[['id', 'ratings', 'destination_city']]

@api_view(['GET'])
@permission_classes([AllowAny])
def explore_destination(request): 
    
    user = request.user if request.user.is_authenticated else None

    if user:
        last_booking = Booking.objects.filter(user=user, status='CMP').order_by('-creation_time').first()
        if not last_booking:
            last_booking = Booking.objects.filter(user=user, status='PPD').order_by('-creation_time').first()
        
        if last_booking:
            last_flight = last_booking.outbound_flight
            description = last_flight.description

            flights = Flight.objects.all().values()
            data = pd.DataFrame(flights)

            if data.empty:
                return Response({"error": "No flights data found"}, status=404)

            data.drop([
                'departure_date', 'duration', 'airportDeparture', 'airportArrival',
                'departure_city', 'Airplane', 'departure_country', 'destination_country',
                'economy_remaining', 'first_remaining', 'business_remaining', 'price_flight',
                'notes'
            ], axis=1, inplace=True, errors='ignore')

            data['description'] = data['description'].str.lower()
            data['destination_city'] = data['destination_city'].str.lower()

            recommendations = recommender_by_description(description, data)
            recommendations_list = recommendations.to_dict(orient='records')
            return Response(recommendations_list)
        else:
            
            return recommend_based_on_ratings()

    
    return recommend_based_on_ratings()

def recommend_based_on_ratings():
    
    now = timezone.now()
    
    high_rated_flights = Flight.objects.filter(ratings=5, departure_date__gte=now).order_by('departure_date')
    
    if not high_rated_flights.exists():
        
        return Response({"error": "No high-rated upcoming flights found"}, status=404)
    
    serialized_flights = FlightSerializer(high_rated_flights, many=True).data
    
    return Response(serialized_flights)

'''