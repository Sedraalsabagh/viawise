from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Hotel
from .serializers import HotelSerializer
from .filters import HotelFilter

@api_view(['GET'])
def hotel(request, star_rating):
    hotels = Hotel.objects.filter(star_rating=star_rating)
    serializer = HotelSerializer(hotels, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def hotel_list(request):
    hotels = Hotel.objects.order_by('-star_rating')
    serializer = HotelSerializer(hotels, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def hotels_filter(request):
    filterset = HotelFilter(request.GET, queryset=Hotel.objects.all().order_by('-star_rating'))
    serializer = HotelSerializer(filterset.qs, many=True)
    return Response(serializer.data)
    
    '''
    
    @api_view(['GET'])  
def get_all(request) :
   filterset=FlightsFilter(request.GET,queryset=Flight.objects.all().order_by('id')) #غيرتي من Flight to FlightSeatType
   serializer=FlightSerializer(filterset.qs ,many=True)
   return Response({"flights":serializer.data}) '''