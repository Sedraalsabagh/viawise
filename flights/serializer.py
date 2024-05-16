from rest_framework import serializers
from .models import *
'''
class FlightSerializer(serializers.ModelSerializer) :
    
    reviws=serializers.SerializerMethodField(method_name='get_reviews',read_only=True)
    class Meta:
        model=Flight
        fields="all"

    def get_reviews(self,obj):
        reviews=obj.reviews.all()
        serializer=ReviewSerializer(reviews,many=True)
        return serializer.data
'''    
class ReviewSerializer(serializers.ModelSerializer) : 
    class Meta:
       
        model=Review
        fields='__all__'

class FlightSerializer(serializers.ModelSerializer) :
    
    class Meta:
        model=Flight
        fields='__all__'       


#RS
class FlightSerializerrs(serializers.ModelSerializer) :
    
    class Meta:
        model=Flight
        fields=['departure_date','price_flight', 'destination_activity', 'destination_climate','destination_type','departure_city']       



class SeatSerializer(serializers.ModelSerializer):
    class Meta:
        model =SeatType
        fields = ['id', 'seat_number', 'is_reserved']
        
class OfferSerializer(serializers.ModelSerializer):
    flight = FlightSerializer()
    
    class Meta:
        model = Offer
        fields = '__all__'        


class FlightProfileSerializer(serializers.ModelSerializer):
    airline_name = serializers.CharField(source='Airplane.airline.airline_name', read_only=True)

    class Meta:
        model = Flight
        fields = ['id','notes','ratings','departure_date', 'airportDeparture', 'airportArrival', 'departure_city', 'destination_city', 'departure_country', 'destination_country', 'price_flight', 'airline_name']


