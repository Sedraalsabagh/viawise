# booking/tests.py

from django.test import TestCase
from django.utils import timezone
from datetime import timedelta, datetime
from decimal import Decimal
from theaccount.models import User
from flights.models import Flight, Airplane 
from .models import Passenger, Booking, Payment

class BookingModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.passenger = Passenger.objects.create(
            first_name="John",
            last_name="Doe",
            gender="Mr",
            date_of_birth="1980-01-01",
            passport_number="A12345678"
        )
        
        # إنشاء كائن Airplane وهمي
        self.airplane = Airplane.objects.create(
            name='Test Airplane',
            manufacturer='Test Manufacturer',
            capacity=100
        )
        

        self.flight = Flight.objects.create(
            departure_date=timezone.now() + timedelta(days=1),
            duration=timedelta(hours=2),
            airportDeparture="JFK",
            airportArrival="LAX",
            departure_city="New York",
            destination_city="Los Angeles",
            departure_country="USA",
            destination_country="USA",
            economy_remaining=100,
            business_remaining=50,
            first_remaining=10,
            price_flight=Decimal('300.00'),
            airplane=self.airplane  
        )

    def test_booking_creation(self):
        booking = Booking.objects.create(
            user=self.user,
            Passenger=self.passenger,
            outbound_flight=self.flight,
            passenger_class='Economy',
            trip_type='OW',
            status='PPD',
            total_cost=Decimal('300.00')
        )
        self.assertEqual(booking.user, self.user)
        self.assertEqual(booking.Passenger, self.passenger)
        self.assertEqual(booking.outbound_flight, self.flight)
        self.assertEqual(booking.passenger_class, 'Economy')
        self.assertEqual(booking.trip_type, 'OW')
        self.assertEqual(booking.status, 'PPD')
        self.assertEqual(booking.total_cost, Decimal('300.00'))



class PaymentModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.passenger = Passenger.objects.create(
            first_name="John",
            last_name="Doe",
            gender="Mr",
            date_of_birth="1980-01-01",
            passport_number="A12345678"
        )

        self.airplane = Airplane.objects.create(
            name='Test Airplane',
            manufacturer='Test Manufacturer',
            capacity=100
        )


        self.flight = Flight.objects.create(
            departure_date=timezone.now() + timedelta(days=1),
            duration=timedelta(hours=2),
            airportDeparture="JFK",
            airportArrival="LAX",
            departure_city="New York",
            destination_city="Los Angeles",
            departure_country="USA",
            destination_country="USA",
            economy_remaining=100,
            business_remaining=50,
            first_remaining=10,
            price_flight=Decimal('300.00'),
            airplane=self.airplane  
        )

        self.booking = Booking.objects.create(
            user=self.user,
            Passenger=self.passenger,
            outbound_flight=self.flight,
            passenger_class='Economy',
            trip_type='OW',
            status='PPD',
            total_cost=Decimal('300.00')
        )

    def test_payment_creation(self):
        payment = Payment.objects.create(
            amount=Decimal('300.00'),
            booking=self.booking,
            user=self.user
        )
        self.assertEqual(payment.amount, Decimal('300.00'))
        self.assertEqual(payment.booking, self.booking)
        self.assertEqual(payment.user, self.user)
