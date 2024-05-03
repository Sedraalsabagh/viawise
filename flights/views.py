from django.shortcuts import render
from django.shortcuts import render,get_object_or_404 
from rest_framework.decorators import api_view ,permission_classes
from rest_framework.response import Response
from .models import Flight,Airline,SeatType,Review
from rest_framework.pagination import PageNumberPagination
from django.db.models import Avg
from .serializer import FlightSerializer,SeatSerializer,ReviewSerializer,OfferSerializer
from .filters import FlightsFilter
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

# Create your views here.
@api_view(['GET'])
def get_all_flights(request) :
    flights=Flight.objects.all()
    serializer=FlightSerializer(flights,many=True)
    print(flights)
    return Response({"flights":serializer.data}) 


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




class SeedDatabaseAPIView(APIView):
    def get(self, request, format=None):
        try:
            # استدعاء الأمر لتشغيل عملية ملء قاعدة البيانات
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
def create_review(request,pk):
    user=request.user
    flight=get_object_or_404(Flight,id=pk)
    data=request.data
    review=flight.reviews.filter(user=user)
    
    if data['rating']<=0 or data['rating']>5:
        flight=Flight.object.create(**data,user=request.user)
        res=FlightSerializer(flight,many=False)
        
        return Response({"error":'please select between 1 to 5 only'},status=status.HTTP_400_BAD_REQUEST)
    elif review.exists():
        new_review={'rating':data['rating'],'comment':data['comment']}
        review.update(**new_review)
        
        rating=flight.reviws.aggregate(avg_ratings=Avg('rating'))
        flight.ratings=rating['avg_ratings']
        flight.save()
        return Response({'details':'Flight review updated'})
    else:
            Review.objects.create(
                user=user,
                flight=flight,
                rating=data['rating'],
                comment=data['comment']
            )
            rating=flight.reviews.aggregate(avg_ratings=Avg('rating'))
            flight.ratings=rating['avg_ratings']
            flight.save()
            return Response({'details':'flight review created'})


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