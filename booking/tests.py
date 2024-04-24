from django.test import TestCase
from .models import Passenger, Baggage, Booking
from flights.models import Flight
from account.models import User  
from datetime import datetime

class TestPassengerModel(TestCase):
    def test_passenger_str(self):
        passenger = Passenger.objects.create(
            first_name='John',
            last_name='Doe',
            gender='Mr',
            date_of_birth=datetime.now().date(),
            passport_number='AB123456'
        )
        self.assertEqual(str(passenger), 'John Doe')

    def test_add_baggage(self):
        passenger = Passenger.objects.create(
            first_name='John',
            last_name='Doe',
            gender='Mr',
            date_of_birth=datetime.now().date(),
            passport_number='AB123456'
        )
        passenger.add_baggage(baggage_type='HI')
        self.assertTrue(passenger.has_baggage(baggage_type='HI'))
        self.assertFalse(passenger.has_baggage(baggage_type='CB'))

class TestBaggageModel(TestCase):
    def test_baggage_str(self):
        passenger = Passenger.objects.create(
            first_name='John',
            last_name='Doe',
            gender='Mr',
            date_of_birth=datetime.now().date(),
            passport_number='AB123456'
        )
        baggage = Baggage.objects.create(
            passenger=passenger,
            baggage_type='HI'
        )
        self.assertEqual(str(baggage), "John Doe's Hand Item")

class TestBookingModel(TestCase):
    def test_booking_str(self):
        booking = Booking.objects.create(
            user=None,
            passenger=None,  
            outbound_flight=None,
            return_flight=None,
            trip_type='OW',
            status='PPD'
        )
        self.assertTrue(str(booking.booking_id))
