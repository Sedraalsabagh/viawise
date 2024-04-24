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





# views.py
from django.http import JsonResponse
from django.core.management import call_command

def load_seed_data(request):
    if request.method == 'POST':
        call_command('load_seed_data')
        return JsonResponse({'message': 'Seed data loading initiated'}, status=200)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)

'''

@api_view(['POST'])
def send_notification(request):
    if request.method == 'POST':
        booking_id = request.data.get('booking_id')
        
        # Check if there is an existing booking based on the booking id
        try:
            booking = Booking.objects.get(pk=booking_id)
            
            # Get the user id associated with the booking
            user_id = booking.user_id
            
            # Get the trip name
            trip_name = f"{booking.outbound_flight.departure_city} to {booking.outbound_flight.destination_city}"
            
            # Look for the FCM token associated with the user
            try:
                push_notification_token = PushNotificationToken.objects.get(owner_id=user_id)
                fcm_token = push_notification_token.fcm_token
                
                # Send the notification using the available data
                fcm_url = 'https://fcm.googleapis.com/fcm/send'
                headers = {
                    'Authorization': 'key=ac5e97f45f4432311f20ab40bfb303455548b52a',
                    'Content-Type': 'application/json'
                }
                data = {
                    'to': fcm_token,
                    'notification': {
                        'title': 'Trip Reminder',
                        'body': f"Don't forget your trip {trip_name} tomorrow!"
                    }
                }
                response = requests.post(fcm_url, headers=headers, json=data)

                return Response({'message': 'Notification sent successfully'})
                
            except PushNotificationToken.DoesNotExist:
                return Response({'error': 'No FCM token available for this user'})
        
        except Booking.DoesNotExist:
            return Response({'error': 'No available booking with this id'})

'''
'''

@api_view(['POST'])
def Bookingview(request):
    if request.method == 'POST':
        # Retrieve flight data
        outbound_flight_id = request.data.get('outbound_flight')
        return_flight_id = request.data.get('return_flight')
        
        passport_number = request.data.get('passenger').get('passport_number')
        existing_passenger = Passenger.objects.filter(passport_number=passport_number).first()
        
        if existing_passenger: 
            booking_data = {
                'user': request.user.id,  
                'passengers': [existing_passenger.id],  # Change 'Passenger' to 'passengers'
                'outbound_flight_id': outbound_flight_id,
                'return_flight_id': return_flight_id,
                'trip_type': request.data.get('trip_type')
            }
            
            booking_serializer = BookingSerializer(data=booking_data)
            if booking_serializer.is_valid():
                booking = booking_serializer.save()
                return Response({"message": "Booking created successfully", "booking": booking_serializer.data}, status=status.HTTP_201_CREATED)
            else:
                return Response(booking_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:  # If passenger doesn't exist, create passenger and booking
            passenger_serializer = PassengerSerializer(data=request.data.get('passenger'))
            if passenger_serializer.is_valid():
                passenger = passenger_serializer.save()
                
                # Create Booking object
                booking_data = {
                    'user': request.user.id,  # Assuming user is authenticated
                    'passengers': [passenger.id],  # Change 'Passenger' to 'passengers'
                    'outbound_flight_id': outbound_flight_id,
                    'return_flight_id': return_flight_id,
                    'trip_type': request.data.get('trip_type')
                }
                
                booking_serializer = BookingSerializer(data=booking_data)
                if booking_serializer.is_valid():
                    booking = booking_serializer.save()
                    return Response({"message": "Booking created successfully", "booking": booking_serializer.data}, status=status.HTTP_201_CREATED)
                else:
                    passenger.delete()
                    return Response(booking_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(passenger_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
'''
'''

class BookingView(APIView):

    def post(self, request):
        serializer = FlightBookingSerializer(data=request.data)
        if serializer.is_valid():
            # Assign current user to booking
            serializer.validated_data['user'] = request.user

            # Check if it's a round trip booking
            trip_type = serializer.validated_data.get('trip_type')
            if trip_type == 'RT':
                # If it's a round trip, make sure both outbound and return flights are provided
                outbound_flight = serializer.validated_data.get('outbound_flight')
                return_flight = serializer.validated_data.get('return_flight')
                if not outbound_flight or not return_flight:
                    return Response({"error": "Both outbound and return flights are required for round trip booking"},
                                    status=status.HTTP_400_BAD_REQUEST)

            # Save the booking
            booking = serializer.save()

            # Check if companions are provided in the request data
            passengers_data = request.data.get('passengers', [])
            
            # Validate passengers
            try:
                self.validate_passengers(passengers_data, booking)
            except ValidationError as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

            for passenger_data in passengers_data:
                # Check if the passenger already exists in the booking
                passport_number = passenger_data.get('passport_number')
                if booking.passengers.filter(passport_number=passport_number).exists():
                    return Response({"error": f"Passenger with passport number {passport_number} is already booked in this flight"},
                                    status=status.HTTP_400_BAD_REQUEST)

                # Check if the passenger already exists in the database
                if Passenger.objects.filter(passport_number=passport_number).exists():
                    return Response({"error": f"Passenger with passport number {passport_number} already exists"},
                                    status=status.HTTP_400_BAD_REQUEST)

                passenger_serializer = PassengerSerializer(data=passenger_data)
                if passenger_serializer.is_valid():
                    passenger_serializer.save(booking=booking)
                else:
                    return Response(passenger_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def validate_passengers(self, passengers_data, booking):
        # Additional validation logic can be added here if needed
        for passenger_data in passengers_data:
            passport_number = passenger_data.get('passport_number')
            if booking.passengers.filter(passport_number=passport_number).exists():
                raise ValidationError(f"Passenger with passport number {passport_number} is already booked in this flight")

'''
'''
class BookingView(APIView):
    def post(self, request):
        serializer = FlightBookingSerializer(data=request.data)
        if serializer.is_valid():
            # Assign current user to booking
            serializer.validated_data['user'] = request.user

            # Check if it's a round trip booking
            trip_type = serializer.validated_data.get('trip_type')
            if trip_type == 'RT':
                # If it's a round trip, make sure both outbound and return flights are provided
                outbound_flight = serializer.validated_data.get('outbound_flight')
                return_flight = serializer.validated_data.get('return_flight')
                if not outbound_flight or not return_flight:
                    return Response({"error": "Both outbound and return flights are required for round trip booking"},
                                    status=status.HTTP_400_BAD_REQUEST)

            # Save the booking
            booking = serializer.save()

            # Check if companions are provided in the request data
            passengers_data = request.data.get('passengers', [])
            for passenger_data in passengers_data:
                passenger_serializer = PassengerSerializer(data=passenger_data)
                if passenger_serializer.is_valid():
                    passenger_serializer.save(booking=booking)
                else:
                    return Response(passenger_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    #new

    def validate_passengers(self, passengers_data):
        passenger_ids = [passenger_data.get('passport_number') for passenger_data in passengers_data]
        if len(passenger_ids) != len(set(passenger_ids)):
            raise ValidationError("Passenger with the same passport number cannot book the same flight multiple times")

        #else:
         #return Response({"message": "Booking successful"})

'''
'''
    def post(self, request):
        ...

        # Check if companions are provided in the request data
        passengers_data = request.data.get('passengers', [])
        self.validate_passengers(passengers_data)

        ...
'''



class PassengerViewSet(viewsets.ModelViewSet):
    queryset = Passenger.objects.prefetch_related('baggages')
    serializer_class = PassengerSerializer
