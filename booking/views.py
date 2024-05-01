from django.shortcuts import render
from rest_framework import status
from rest_framework import viewsets
from rest_framework.views import APIView
from .models import Booking,Passenger,Payment#,PushNotificationToken
from .serializers import BookingSerializer,PassengerSerializer,PassengerSerializer
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import api_view ,permission_classes
from flights.models import Flight
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view
from django.http import JsonResponse
from django.core.management import call_command



@api_view(['POST'])
def create_booking(request):
    if request.method == 'POST':
        booking_data = request.data.get('booking', {})
        passengers_data = request.data.get('passengers', [])  # Accept list of passengers
        
        if not booking_data or not passengers_data:
            return Response({'message': 'Booking and Passengers data are required'}, status=status.HTTP_400_BAD_REQUEST)
        
        outbound_flight_id = booking_data.get('outbound_flight')
        return_flight_id = booking_data.get('return_flight') 
        
        if outbound_flight_id == return_flight_id:
            return Response({'message': 'Outbound and return flights cannot be the same'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            outbound_flight = Flight.objects.get(id=outbound_flight_id)
            return_flight = Flight.objects.get(id=return_flight_id)
        except Flight.DoesNotExist:
            return Response({'message': 'One of the flights does not exist'}, status=status.HTTP_404_NOT_FOUND)
        
        booking_serializer = BookingSerializer(data=booking_data)
        if not booking_serializer.is_valid():
            return Response(booking_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        bookings = []
        successful_bookings = []
        unsuccessful_bookings = []
        for passenger_data in passengers_data:
            passport_number = passenger_data.get('passport_number')
            matching_passengers = Passenger.objects.filter(passport_number=passport_number)
            
            if matching_passengers.exists():
                passenger = matching_passengers.first()
            else:
                passenger_serializer = PassengerSerializer(data=passenger_data)
                if not passenger_serializer.is_valid():
                    return Response(passenger_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                
                passenger = passenger_serializer.save()
            
            booking_exists = Booking.objects.filter(Passenger=passenger.id, outbound_flight=outbound_flight, return_flight=return_flight).exists()
            if booking_exists:
                unsuccessful_bookings.append(passenger.id)
            else:
                booking_data['Passenger'] = passenger.id
                booking_serializer = BookingSerializer(data=booking_data)
                if not booking_serializer.is_valid():
                    return Response(booking_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                
                booking = booking_serializer.save()
                bookings.append(booking.id)
                successful_bookings.append(passenger.id)
        
        response_data = {
            'message': 'Bookings created successfully',
            'successful_booking_passengers': successful_bookings,
            'unsuccessful_booking_passengers': unsuccessful_bookings,
            'booking_ids': bookings
        }
        return Response(response_data, status=status.HTTP_201_CREATED)
    
@api_view(['POST'])
def create_booking(request):
    if request.method == 'POST':
        booking_data = request.data.get('booking', {})
        passengers_data = request.data.get('passengers', [])  # Accept list of passengers
        
        if not booking_data or not passengers_data:
            return Response({'message': 'Booking and Passengers data are required'}, status=status.HTTP_400_BAD_REQUEST)
        
        outbound_flight_id = booking_data.get('outbound_flight')
        return_flight_id = booking_data.get('return_flight') 
        
        if outbound_flight_id == return_flight_id:
            return Response({'message': 'Outbound and return flights cannot be the same'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            outbound_flight = Flight.objects.get(id=outbound_flight_id)
            return_flight = Flight.objects.get(id=return_flight_id)
        except Flight.DoesNotExist:
            return Response({'message': 'One of the flights does not exist'}, status=status.HTTP_404_NOT_FOUND)
        
        # Check if there's an offer for the outbound flight
        outbound_offer = outbound_flight.offer_set.first()
        outbound_discount = 0
        if outbound_offer:
            outbound_discount = outbound_offer.discount_percentage
        
        # Check if there's an offer for the return flight
        return_offer = return_flight.offer_set.first()
        return_discount = 0
        if return_offer:
            return_discount = return_offer.discount_percentage
        
        booking_serializer = BookingSerializer(data=booking_data)
        if not booking_serializer.is_valid():
            return Response(booking_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        bookings = []
        successful_bookings = []
        unsuccessful_bookings = []
        for passenger_data in passengers_data:
            passport_number = passenger_data.get('passport_number')
            matching_passengers = Passenger.objects.filter(passport_number=passport_number)
            
            if matching_passengers.exists():
                passenger = matching_passengers.first()
            else:
                passenger_serializer = PassengerSerializer(data=passenger_data)
                if not passenger_serializer.is_valid():
                    return Response(passenger_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                
                passenger = passenger_serializer.save()
            
            booking_exists = Booking.objects.filter(Passenger=passenger.id, outbound_flight=outbound_flight, return_flight=return_flight).exists()
            if booking_exists:
                unsuccessful_bookings.append(passenger.id)
            else:
                booking_data['Passenger'] = passenger.id
                booking_serializer = BookingSerializer(data=booking_data)
                if not booking_serializer.is_valid():
                    return Response(booking_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                
                # Calculate final price after applying discounts
                price = booking_data.get('price')
                price -= (price * outbound_discount) / 100
                price -= (price * return_discount) / 100
                booking_data['price'] = price
                
                booking = booking_serializer.save()
                bookings.append(booking.id)
                successful_bookings.append(passenger.id)
        
        response_data = {
            'message': 'Bookings created successfully',
            'successful_booking_passengers': successful_bookings,
            'unsuccessful_booking_passengers': unsuccessful_bookings,
            'booking_ids': bookings
        }
        return Response(response_data, status=status.HTTP_201_CREATED)
    

        
@api_view(['POST'])
def make_payment(request):
    booking_id = request.data.get('booking_id')

    try:
        booking = Booking.objects.get(id=booking_id)
    except Booking.DoesNotExist:
        return Response({"message": "Booking does not exist."}, status=status.HTTP_404_NOT_FOUND)

    user = booking.user
    total_cost = booking.total_cost

    if user.balance is not None and total_cost is not None:
        if user.balance >= total_cost:
            payment = Payment.objects.create(
                amount=total_cost,
                booking=booking,
                user=user
            )
            user.balance -= total_cost
            user.save()
            
            booking.status = 'CMP'
            booking.save()

            return Response({"message": "Payment created successfully."}, status=status.HTTP_201_CREATED)
        else:
            return Response({"message": "Insufficient balance."}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({"message": "Invalid balance or total cost."}, status=status.HTTP_400_BAD_REQUEST)
        
class UserBookingsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_bookings = Booking.objects.filter(user=request.user)
        serializer = BookingSerializer(user_bookings, many=True)
        return Response(serializer.data)








def load_seed_data(request):
    if request.method == 'POST':
        call_command('load_seed_data')
        return JsonResponse({'message': 'Seed data loading initiated'}, status=200)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)




class PassengerViewSet(viewsets.ModelViewSet):
    queryset = Passenger.objects.prefetch_related('baggages')
    serializer_class = PassengerSerializer
    
    
@api_view(['POST'])
def cancel_booking(request):
    if request.method == 'POST':
        
        data = request.data
        username = data.get('username') #password 
        password = data.get('password')
        booking_id = data.get('booking_id')

        
        if not all([username, password, booking_id]):
            return JsonResponse({'success': False, 'message': 'Missing required fields.'})

        
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Invalid username or password.'})

        if not check_password(password, user.password):
            return JsonResponse({'success': False, 'message': 'Invalid username or password.'})

        
        try:
            booking = Booking.objects.get(id=booking_id)
        except Booking.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Booking not found.'})

        
        if booking.user != user:
            return JsonResponse({'success': False, 'message': 'Unauthorized access to booking cancellation.'})

        if booking.status != 'CMP':
            return JsonResponse({'success': False, 'message': 'The booking is not completed.'})

        
        try:
            policy = PolicyAgency.objects.get()
        except PolicyAgency.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'PolicyAgency not found.'})

        
        if not policy.cancellable:
            return JsonResponse({'success': False, 'message': 'Booking cancellation not allowed.'})

        
        cancellation_period = policy.cancel_period

        
        if cancellation_period > timedelta(days=0):
            time_difference = timezone.now() - booking.booking_date
            if time_difference > cancellation_period:
                return JsonResponse({'success': False, 'message': 'Cancellation period expired.'})

        
        booking.status = 'CNL'
        booking.save()

        
        refund_amount = booking.total_cost * policy.cancellation_discount_amount

        
        user.balance += refund_amount
        user.save()

        return JsonResponse({'success': True, 'message': 'Booking canceled successfully. Refund amount: {}'.format(refund_amount)})
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method.'})    
