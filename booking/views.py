from django.shortcuts import render
from rest_framework import status
from rest_framework import viewsets
from rest_framework.views import APIView
from .models import Booking,Passenger,Payment,AgencyPolicy
from .serializers import BookingSerializer,PassengerSerializer,PassengerSerializer,AgencyPolicySerializer
from .serializers import *
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import api_view ,permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view
from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from .models import Booking
from .serializers import BookingSerializer,PriavateSerializer1
from django.core.management import call_command
from theaccount.models import *
from flights.models import *
from rest_framework import generics
from django.http import JsonResponse
from django.contrib.auth.hashers import check_password
from datetime import timedelta
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import datetime
from decimal import Decimal
# from celery import shared_task #




    

    

        
@api_view(['POST'])
def make_paymentt(request): #true
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
        serializer = BookingSerializer3(user_bookings, many=True)
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
    
    
from datetime import timedelta

@api_view(['POST'])
def cancel_booking(request):
    if request.method == 'POST':
        data = request.data
        username = data.get('username')
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
            flight = Flight.objects.get(id=booking.outbound_flight_id)
        except Flight.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Flight not found.'})

        cancellation_period = flight.departure_date - timezone.now().date()

        if cancellation_period <= timedelta(days=7):
            try:
                policy = AgencyPolicy.objects.get(policy_type='cancel')
            except AgencyPolicy.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'Cancellation policy not found.'})

        else:
            try:
                policy = AgencyPolicy.objects.get(policy_type='cancel_over_week')
            except AgencyPolicy.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'Cancellation policy for over a week not found.'})

        refund_amount = booking.total_cost * (policy.percentage / 100)

        booking.status = 'CNL'
        booking.save()

        user.balance += refund_amount
        user.save()

        
        passenger_class = booking.passenger_class
        outbound_flight = booking.outbound_flight
        if passenger_class == 'Economy':
            outbound_flight.economy_remaining += 1
        elif passenger_class == 'Business':
            outbound_flight.business_remaining += 1
        elif passenger_class == 'First':
            outbound_flight.first_remaining += 1
        outbound_flight.save()

        return_flight = booking.return_flight
        if return_flight:
            if passenger_class == 'Economy':
                return_flight.economy_remaining += 1
            elif passenger_class == 'Business':
                return_flight.business_remaining += 1
            elif passenger_class == 'First':
                return_flight.first_remaining += 1
            return_flight.save()

        return JsonResponse({'success': True, 'message': 'Booking canceled successfully. Refund amount: {}'.format(refund_amount)})
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method.'})

    

@api_view(['POST'])
def make_payment(request):
    booking_id = request.data.get('booking_id')

    try:
        booking = Booking.objects.get(id=booking_id)
    except Booking.DoesNotExist:
        return Response({"message": "Booking does not exist."}, status=status.HTTP_404_NOT_FOUND)

    user = booking.user
    total_cost = booking.total_cost

    policy = AgencyPolicy.objects.filter(policy_type='offers').first()

    if not policy:
        return Response({"message": "No valid policy found."}, status=status.HTTP_404_NOT_FOUND)

    if user.balance is None or total_cost is None:
        return Response({"message": "Invalid account or booking details."}, status=status.HTTP_400_BAD_REQUEST)

    if user.balance < total_cost:
        return Response({"message": "Insufficient balance."}, status=status.HTTP_400_BAD_REQUEST)

    payment = Payment.objects.create(
        amount=total_cost,
        booking=booking,
        user=user
    )

    user.pointBalance += policy.points_offers
    
    
    if user.pointBalance >= policy.points:
       
        discount_amount = total_cost * (policy.percentage / 100)
        
        user.balance -= discount_amount
        
        user.pointBalance -= policy.points
        
    else:
        
        user.balance -= total_cost

    
    user.save()

    
    booking.status = 'CMP'
    booking.save()

    return Response({"message": "Payment created successfully."}, status=status.HTTP_201_CREATED)

@api_view(['POST'])
def make_payment(request):
    booking_ids = request.data.get('booking_ids', [])
    successful_payments = []
    errors = []

    for booking_id in booking_ids:
        try:
            booking = Booking.objects.get(id=booking_id)
            user = booking.user
            total_cost = booking.total_cost

            policy = AgencyPolicy.objects.filter(policy_type='offers').first()

            if not policy:
                errors.append({"booking_id": booking_id, "message": "No valid policy found."})
                continue

            if user.balance is None or total_cost is None:
                errors.append({"booking_id": booking_id, "message": "Invalid account or booking details."})
                continue

            if user.balance < total_cost:
                errors.append({"booking_id": booking_id, "message": "Insufficient balance."})
                continue

            payment = Payment.objects.create(
                amount=total_cost,
                booking=booking,
                user=user
            )

            user.pointBalance += policy.points_offers

            if user.pointBalance >= policy.points:
                discount_amount = total_cost * (policy.percentage / 100)
                user.balance -= discount_amount
                user.pointBalance -= policy.points
            else:
                user.balance -= total_cost

            user.save()
            booking.status = 'CMP'
            booking.save()

            successful_payments.append(booking_id)

        except Booking.DoesNotExist:
            errors.append({"booking_id": booking_id, "message": "Booking does not exist."})

    if successful_payments:
        message = f"Payment successfully created for booking IDs: {successful_payments}"
        status_code = status.HTTP_201_CREATED
    else:
        message = "No payments were created."
        status_code = status.HTTP_400_BAD_REQUEST

    return Response({
        "message": message,
        "errors": errors
    }, status=status_code)





@api_view(['POST'])
def booking(request): #جد هاد الصج  #اكتر من حدا 
    if request.method == 'POST':
        booking_data = request.data.get('booking', {})
        passenger_data = request.data.get('passenger', {})
        
        if not booking_data or not passenger_data:
            return Response({'message': 'Booking and Passenger data are required'}, status=status.HTTP_400_BAD_REQUEST)
        
        outbound_flight_id = booking_data.get('outbound_flight')
        return_flight_id = booking_data.get('return_flight') 
        

        if outbound_flight_id == return_flight_id:
            return Response({'message': 'Outbound and return flights cannot be the same'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            outbound_flight = Flight.objects.get(id=outbound_flight_id)
            #return_flight = Flight.objects.get(id=return_flight_id)
        except Flight.DoesNotExist:
            return Response({'message': 'One of the flights does not exist'}, status=status.HTTP_404_NOT_FOUND)
        
        passport_number = passenger_data.get('passport_number')
        matching_passengers = Passenger.objects.filter(passport_number=passport_number)
        
        if matching_passengers.exists():
            passenger = matching_passengers.first()
        else:
            
            passenger_serializer = PassengerSerializer(data=passenger_data)
            if passenger_serializer.is_valid():
                passenger = passenger_serializer.save()
            else:
                return Response(passenger_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        for booking in Booking.objects.filter(Passenger=passenger.id):
            if booking.outbound_flight_id == outbound_flight_id or (booking.return_flight_id and booking.return_flight_id == return_flight_id):
               return Response({'message': 'Passenger already booked on one of these flights'}, status=status.HTTP_400_BAD_REQUEST)
        booking_data['Passenger'] = passenger.id
        booking_serializer = BookingSerializer(data=booking_data)
        if booking_serializer.is_valid():
            booking = booking_serializer.save()
            return Response({'message': 'Booking created successfully', 'booking_id': booking.id}, status=status.HTTP_201_CREATED)
        return Response(booking_serializer.errors, status=status.HTTP_400_BAD_REQUEST)   

'''
@shared_task
def update_booking_status():
    bookings = Booking.objects.filter(status='PPD')  
    for booking in bookings:
        
        policy = AgencyPolicy.objects.get(policy_type='cancel_without_payment')
        
        cancel_time = booking.creation_time + policy.duration
        
        if timezone.now() > cancel_time:
            
            booking.status = 'CNL'
            booking.save()
'''            

@api_view(['PATCH'])
def modify_booking1(request, booking_id):
    try:
        booking = Booking.objects.get(pk=booking_id)
    except Booking.DoesNotExist:
        return Response({'error': 'Booking not found'}, status=status.HTTP_404_NOT_FOUND)

    
    if booking.status != 'CMP':
        return Response({'error': 'Only completed bookings can be modified'}, status=status.HTTP_400_BAD_REQUEST)

    outbound_flight_id = request.data.get('outbound_flight_id')

    if outbound_flight_id:
        try:
            outbound_flight = Flight.objects.get(pk=outbound_flight_id)
            booking.outbound_flight = outbound_flight
        except Flight.DoesNotExist:
            return Response({'error': 'Outbound flight not found'}, status=status.HTTP_404_NOT_FOUND)
    else:
        return Response({'error': 'Outbound flight ID is required'}, status=status.HTTP_400_BAD_REQUEST)

    booking.save()
    serializer = BookingSerializer(booking)
    return Response({'message': 'Booking updated successfully'}, status=status.HTTP_200_OK)

@api_view(['PATCH'])
def modify_booking(request, booking_id): # اصح شي 
    try:
        booking = Booking.objects.get(pk=booking_id)
    except Booking.DoesNotExist:
        return Response({'error': 'Booking not found'}, status=status.HTTP_404_NOT_FOUND)

    if booking.status != 'CMP':
        return Response({'error': 'Only completed bookings can be modified'}, status=status.HTTP_400_BAD_REQUEST)

    outbound_flight_id = request.data.get('outbound_flight_id')
    if outbound_flight_id:
        try:
            outbound_flight = Flight.objects.get(pk=outbound_flight_id)
            booking.outbound_flight = outbound_flight
        except Flight.DoesNotExist:
            return Response({'error': 'Outbound flight not found'}, status=status.HTTP_404_NOT_FOUND)
    else:
        return Response({'error': 'Outbound flight ID is required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        policy = AgencyPolicy.objects.get(policy_type='modify')
    except AgencyPolicy.DoesNotExist:
        return Response({'error': 'Modification policy not found'}, status=status.HTTP_404_NOT_FOUND)

    if policy:
        modification_fee = booking.total_cost * policy.percentage / 100

        if modification_fee > booking.user.balance:
            return Response({'error': 'Insufficient balance'}, status=status.HTTP_400_BAD_REQUEST)

        
        booking.user.balance -= modification_fee
        booking.user.save()

     
        payment = Payment.objects.filter(booking=booking).first()
        if payment:
            payment.amount += modification_fee  
            payment.save()
        else:
           
            payment = Payment.objects.create(
                amount=modification_fee,
                payment_date=timezone.now(),
                booking=booking,
                user=booking.user
            )

        
        if booking.outbound_flight.economy_remaining > 0:
            booking.outbound_flight.economy_remaining -= 1
            booking.outbound_flight.save()
            if booking.return_flight:
                booking.return_flight.economy_remaining += 1
                booking.return_flight.save()

        booking.save()
        return Response({'message': 'Booking updated successfully'}, status=status.HTTP_200_OK)


from django.db.models import F 

@api_view(['PATCH'])
def modify_booking(request, booking_id):
    try:
        booking = Booking.objects.get(pk=booking_id)
    except Booking.DoesNotExist:
        return Response({'error': 'Booking not found'}, status=status.HTTP_404_NOT_FOUND)

    if booking.status != 'CMP':
        return Response({'error': 'Only completed bookings can be modified'}, status=status.HTTP_400_BAD_REQUEST)

    outbound_flight_id = request.data.get('outbound_flight_id')
    if outbound_flight_id:
        try:
            new_outbound_flight = Flight.objects.get(pk=outbound_flight_id)
        except Flight.DoesNotExist:
            return Response({'error': 'Outbound flight not found'}, status=status.HTTP_404_NOT_FOUND)
    else:
        return Response({'error': 'Outbound flight ID is required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        policy = AgencyPolicy.objects.get(policy_type='modify')
    except AgencyPolicy.DoesNotExist:
        return Response({'error': 'Modification policy not found'}, status=status.HTTP_404_NOT_FOUND)

    modification_fee = booking.total_cost * policy.percentage / 100
    if modification_fee > booking.user.balance:
        return Response({'error': 'Insufficient balance'}, status=status.HTTP_400_BAD_REQUEST)

    booking.user.balance -= modification_fee
    booking.user.save()

    
    payment = Payment.objects.filter(booking=booking).first()
    if payment:
        payment.amount += modification_fee  
        payment.save()
    else:
        payment = Payment.objects.create(
            amount=modification_fee,
            payment_date=timezone.now(),
            booking=booking,
            user=booking.user
        )

    
    class_attr = f"{booking.passenger_class.lower()}_remaining" 
    Flight.objects.filter(id=booking.outbound_flight.id).update(**{class_attr: F(class_attr) + 1})
    Flight.objects.filter(id=new_outbound_flight.id).update(**{class_attr: F(class_attr) - 1})

    
    booking.outbound_flight = new_outbound_flight
    booking.save()

    return Response({'message': 'Booking updated successfully'}, status=status.HTTP_200_OK)





class AllBookingsAPIView(generics.ListAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    
    
    



@api_view(['GET'])
def Agency_condition(request, policy_type):
    try:
        policy = AgencyPolicy.objects.get(policy_type=policy_type)
        serializer = AgencyPolicySerializer(policy)
        return Response(serializer.data)
    except AgencyPolicy.DoesNotExist:
        return Response({"message": "Policy not found."}, status=status.HTTP_404_NOT_FOUND)
    
    
    

@api_view(['GET'])
def get_Tickets(request, booking_id):
    try:
        booking = Booking.objects.get(id=booking_id)
    except Booking.DoesNotExist:
        return Response({'message': 'Booking not found'}, status=404)

    serializer = BookingSerializerT(booking)
    return Response(serializer.data)    



@api_view(['GET'])
def all_booking(request):
    bookings = Booking.objects.all()
    serializer = BookingSerializer(bookings, many=True)
    return Response(serializer.data)





@api_view(['POST'])
@permission_classes([IsAuthenticated])
def booking(request): 
    
    if request.method == 'POST':
        user_id = request.user.id  # استخراج معرف المستخدم المصادق عليه من request.user
        
        booking_data = request.data.get('booking', {})
        passenger_data = request.data.get('passenger', {})
        
        if not booking_data or not passenger_data:
            return Response({'message': 'Booking and Passenger data are required'}, status=status.HTTP_400_BAD_REQUEST)
        
        outbound_flight_id = booking_data.get('outbound_flight')
        return_flight_id = booking_data.get('return_flight') 
        

        if outbound_flight_id == return_flight_id:
            return Response({'message': 'Outbound and return flights cannot be the same'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            outbound_flight = Flight.objects.get(id=outbound_flight_id)
            #return_flight = Flight.objects.get(id=return_flight_id)
        except Flight.DoesNotExist:
            return Response({'message': 'One of the flights does not exist'}, status=status.HTTP_404_NOT_FOUND)
        
        passport_number = passenger_data.get('passport_number')
        matching_passengers = Passenger.objects.filter(passport_number=passport_number)
        
        if matching_passengers.exists():
            passenger = matching_passengers.first()
        else:
            
            passenger_serializer = PassengerSerializer(data=passenger_data)
            if passenger_serializer.is_valid():
                passenger = passenger_serializer.save()
            else:
                return Response(passenger_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        for booking in Booking.objects.filter(Passenger=passenger.id):
            if booking.outbound_flight_id == outbound_flight_id or (booking.return_flight_id and booking.return_flight_id == return_flight_id):
               return Response({'message': 'Passenger already booked on one of these flights'}, status=status.HTTP_400_BAD_REQUEST)
        booking_data['Passenger'] = passenger.id
        booking_serializer = BookingSerializer(data=booking_data)
        if booking_serializer.is_valid():
            booking = booking_serializer.save(user_id=user_id)  
            return Response({'message': 'Booking created successfully', 'booking_id': booking.id}, status=status.HTTP_201_CREATED)
        return Response(booking_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def make_booking1(request):
    if request.method == 'POST':
        user_id = request.user.id  

        booking_data = request.data.get('booking', {})
        passengers_data = request.data.get('passenger', []) 

        if not booking_data or not passengers_data:
            return Response({'message': 'Booking and Passenger data are required'}, status=status.HTTP_400_BAD_REQUEST)

        outbound_flight_id = booking_data.get('outbound_flight')
        return_flight_id = booking_data.get('return_flight')

        if outbound_flight_id == return_flight_id:
            return Response({'message': 'Outbound and return flights cannot be the same'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            outbound_flight = Flight.objects.get(id=outbound_flight_id)
           
            return_flight = Flight.objects.get(id=return_flight_id) if return_flight_id else None
        except Flight.DoesNotExist:
            return Response({'message': 'One of the flights does not exist'}, status=status.HTTP_404_NOT_FOUND)

        bookings = []
        for passenger_data in passengers_data:
            passport_number = passenger_data.get('passport_number')
            passenger, created = Passenger.objects.get_or_create(
                passport_number=passport_number,
                defaults={k: passenger_data[k] for k in ['first_name', 'last_name', 'gender', 'date_of_birth']}
            )

          
            if Booking.objects.filter(Passenger=passenger, outbound_flight=outbound_flight, return_flight=return_flight).exists():
                continue  

           
            new_booking = Booking.objects.create(
                user_id=user_id,
                Passenger=passenger,
                outbound_flight=outbound_flight,
                return_flight=return_flight,
                passenger_class=booking_data.get('passenger_class'),
                trip_type=booking_data.get('trip_type'),
                status='PPD'  
            )
            bookings.append(new_booking)

        if not bookings:
            return Response({'message': 'No bookings were created'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'message': f'{len(bookings)} bookings were successfully created'}, status=status.HTTP_201_CREATED)
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def make_booking(request):
    if request.method == 'POST':
        user_id = request.user.id  

        booking_data = request.data
        passengers_data = booking_data.pop('passenger', [])

        if not passengers_data:
            return Response({'message': 'Passenger data is required'}, status=status.HTTP_400_BAD_REQUEST)

        outbound_flight_id = booking_data.get('outbound_flight')
        return_flight_id = booking_data.get('return_flight')

        if outbound_flight_id == return_flight_id:
            return Response({'message': 'Outbound and return flights cannot be the same'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            outbound_flight = Flight.objects.get(id=outbound_flight_id)
           
            return_flight = Flight.objects.get(id=return_flight_id) if return_flight_id else None
        except Flight.DoesNotExist:
            return Response({'message': 'One of the flights does not exist'}, status=status.HTTP_404_NOT_FOUND)

        bookings = []
        for passenger_data in passengers_data:
            passport_number = passenger_data.get('passport_number')
            passenger, created = Passenger.objects.get_or_create(
                passport_number=passport_number,
                defaults={k: passenger_data[k] for k in ['first_name', 'last_name', 'gender', 'date_of_birth']}
            )

          
            if Booking.objects.filter(Passenger=passenger, outbound_flight=outbound_flight, return_flight=return_flight).exists():
                continue  

           
            new_booking = Booking.objects.create(
                user_id=user_id,
                Passenger=passenger,
                outbound_flight=outbound_flight,
                return_flight=return_flight,
                passenger_class=booking_data.get('passenger_class'),
                trip_type=booking_data.get('trip_type'),
                status='PPD'  
            )
            bookings.append(new_booking)

        if not bookings:
            return Response({'message': 'No bookings were created'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'message': f'{len(bookings)} bookings were successfully created'}, status=status.HTTP_201_CREATED)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def make_booking(request):
    if request.method == 'POST':
        user_id = request.user.id  

        booking_data = request.data
        passengers_data = booking_data.pop('passenger', [])

        if not passengers_data:
            return Response({'message': 'Passenger data is required'}, status=status.HTTP_400_BAD_REQUEST)

        outbound_flight_id = booking_data.get('outbound_flight')
        return_flight_id = booking_data.get('return_flight')

        if outbound_flight_id == return_flight_id:
            return Response({'message': 'Outbound and return flights cannot be the same'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            outbound_flight = Flight.objects.get(id=outbound_flight_id)
           
            return_flight = Flight.objects.get(id=return_flight_id) if return_flight_id else None
        except Flight.DoesNotExist:
            return Response({'message': 'One of the flights does not exist'}, status=status.HTTP_404_NOT_FOUND)

        bookings = []
        for passenger_data in passengers_data:
            passport_number = passenger_data.get('passport_number')
            passenger, created = Passenger.objects.get_or_create(
                passport_number=passport_number,
                defaults={k: passenger_data[k] for k in ['first_name', 'last_name', 'gender', 'date_of_birth']}
            )

          
            if Booking.objects.filter(Passenger=passenger, outbound_flight=outbound_flight, return_flight=return_flight).exists():
                continue  

           
            new_booking = Booking.objects.create(
                user_id=user_id,
                Passenger=passenger,
                outbound_flight=outbound_flight,
                return_flight=return_flight,
                passenger_class=booking_data.get('passenger_class'),
                trip_type=booking_data.get('trip_type'),
                status='PPD'  
            )
            bookings.append(new_booking)

        if not bookings:
            return Response({'message': 'No bookings were created'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'message': f'{len(bookings)} bookings were successfully created'}, status=status.HTTP_201_CREATED)
    
from rest_framework import status

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def make_booking(request):
    if request.method == 'POST':
        user_id = request.user.id  

        booking_data = request.data
        passengers_data = booking_data.pop('passenger', [])

        if not passengers_data:
            return Response({'message': 'Passenger data is required'}, status=status.HTTP_400_BAD_REQUEST)

        outbound_flight_id = booking_data.get('outbound_flight')
        return_flight_id = booking_data.get('return_flight')

        if outbound_flight_id == return_flight_id:
            return Response({'message': 'Outbound and return flights cannot be the same'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            outbound_flight = Flight.objects.get(id=outbound_flight_id)
           
            return_flight = Flight.objects.get(id=return_flight_id) if return_flight_id else None
        except Flight.DoesNotExist:
            return Response({'message': 'One of the flights does not exist'}, status=status.HTTP_404_NOT_FOUND)

        bookings = []
        for passenger_data in passengers_data:
            passport_number = passenger_data.get('passport_number')
            passenger, created = Passenger.objects.get_or_create(
                passport_number=passport_number,
                defaults={k: passenger_data[k] for k in ['first_name', 'last_name', 'gender', 'date_of_birth']}
            )

          
            if Booking.objects.filter(Passenger=passenger, outbound_flight=outbound_flight, return_flight=return_flight).exists():
                continue  

           
            new_booking = Booking.objects.create(
                user_id=user_id,
                Passenger=passenger,
                outbound_flight=outbound_flight,
                return_flight=return_flight,
                passenger_class=booking_data.get('passenger_class'),
                trip_type=booking_data.get('trip_type'),
                status='PPD'  
            )
            bookings.append(new_booking)

        if not bookings:
            return Response({'message': 'No bookings were created'}, status=status.HTTP_400_BAD_REQUEST)

        booking_ids = [booking.id for booking in bookings]
        return Response({'message': f'{len(bookings)} bookings were successfully created', 'booking_ids': booking_ids}, status=status.HTTP_201_CREATED)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def make_booking(request):
    if request.method == 'POST':
        user_id = request.user.id  

        booking_data = request.data
        passengers_data = booking_data.pop('passenger', [])

        if not passengers_data:
            return Response({'message': 'Passenger data is required'}, status=status.HTTP_400_BAD_REQUEST)

        outbound_flight_id = booking_data.get('outbound_flight')
        return_flight_id = booking_data.get('return_flight')

        if outbound_flight_id == return_flight_id:
            return Response({'message': 'Outbound and return flights cannot be the same'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            outbound_flight = Flight.objects.get(id=outbound_flight_id)
            return_flight = Flight.objects.get(id=return_flight_id) if return_flight_id else None
        except Flight.DoesNotExist:
            return Response({'message': 'One of the flights does not exist'}, status=status.HTTP_404_NOT_FOUND)

        bookings = []
        for passenger_data in passengers_data:
            passport_number = passenger_data.get('passport_number')
            passenger, created = Passenger.objects.get_or_create(
                passport_number=passport_number,
                defaults={k: passenger_data[k] for k in ['first_name', 'last_name', 'gender', 'date_of_birth']}
            )

            if Booking.objects.filter(Passenger=passenger, outbound_flight=outbound_flight, return_flight=return_flight).exists():
                continue  

            new_booking = Booking.objects.create(
                user_id=user_id,
                Passenger=passenger,
                outbound_flight=outbound_flight,
                return_flight=return_flight,
                passenger_class=booking_data.get('passenger_class'),
                trip_type=booking_data.get('trip_type'),
                status='PPD'  
            )
            bookings.append(new_booking)

        if not bookings:
            return Response({'message': 'No bookings were created'}, status=status.HTTP_400_BAD_REQUEST)
        
        
        created_booking_ids = [booking.id for booking in bookings]

        return Response({'created_booking_ids': created_booking_ids, 'status': 'PPD'}, status=status.HTTP_201_CREATED)     
    
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_point_balance(request):
    user = request.user 
    if not user.is_anonymous:  
        serializer = PriavateSerializer1(user)  
        return Response(serializer.data)  
    else:
        return Response({'error': 'User is not authenticated'}, status=401)    
    
@api_view(['GET'])
def booking_details(request, id_booking):
    try:
        booking = Booking.objects.get(pk=id_booking)
    except Booking.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = BookingSerializer100(booking)
    return Response(serializer.data)