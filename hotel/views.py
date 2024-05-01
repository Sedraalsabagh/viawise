from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Hotel
from .serializers import HotelSerializer

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