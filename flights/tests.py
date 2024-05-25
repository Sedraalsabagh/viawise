from django.test import TestCase, Client
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta
from theaccount.models import User
from flights.models import Flight, Offer
from .models import AgencyPolicy, Passenger, Booking, Payment

class TestAgencyPolicyModel(TestCase):

    def test_agency_policy_creation(self):
        policy = AgencyPolicy.objects.create(
            policy_type='modify',
            percentage=Decimal('10.00'),
            duration=timedelta(days=3),
            points=100,
            points_offers=50,
            conditions='Some conditions'
        )
        self.assertEqual(str(policy), 'modify policy')

class TestPassengerModel(TestCase):

    def test_passenger_creation(self):
        passenger = Passenger.objects.create(
            first_name='Jane',
            last_name='Doe',
            gender='Ms',
            date_of_birth='1992-02-02',
            passport_number='B98765432'
        )
        self.assertEqual(str(passenger), 'Jane Doe')

class TestBookingModel(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.passenger = Passenger.objects.create(
            first_name='John',
            last_name='Doe',
            gender='Mr',
            date_of_birth='1990-01-01',
            passport_number='A12345678'
        )
        self.flight = Flight.objects.create(
            flight_number='XY123',
            departure='2024-06-01 10:00:00',
            arrival='2024-06-01 12:00:00',
            price_flight=Decimal('100.00'),
            economy_remaining=10,
            business_remaining=5,
            first_remaining=2
        )
        self.booking = Booking.objects.create(
            user=self.user,
            Passenger=self.passenger,
            outbound_flight=self.flight,
            passenger_class='Economy',
            trip_type='OW'
        )
        self.offer = Offer.objects.create(
            flight=self.flight,
            discount_percentage=10,
            start_date=timezone.now() - timedelta(days=1),
            end_date=timezone.now() + timedelta(days=1)
        )

    def test_booking_creation(self):
        self.assertEqual(self.booking.status, 'PPD')
        self.assertEqual(self.booking.total_cost, Decimal('100.00'))

    def test_booking_availability(self):
        self.booking.check_availability(self.booking.outbound_flight, self.booking.passenger_class)
        self.flight.economy_remaining = 0
        self.flight.save()
        with self.assertRaises(ValidationError):
            self.booking.check_availability(self.booking.outbound_flight, self.booking.passenger_class)

    def test_booking_cost_calculation(self):
        self.booking.calculate_initial_cost()
        self.assertEqual(self.booking.total_cost, Decimal('100.00'))

    def test_booking_apply_discounts(self):
        self.booking.apply_discounts()
        self.assertEqual(self.booking.total_cost, Decimal('90.00'))

class TestPaymentModel(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.passenger = Passenger.objects.create(
            first_name='John',
            last_name='Doe',
            gender='Mr',
            date_of_birth='1990-01-01',
            passport_number='A12345678'
        )
        self.flight = Flight.objects.create(
            flight_number='XY123',
            departure='2024-06-01 10:00:00',
            arrival='2024-06-01 12:00:00',
            price_flight=Decimal('100.00'),
            economy_remaining=10,
            business_remaining=5,
            first_remaining=2
        )
        self.booking = Booking.objects.create(
            user=self.user,
            Passenger=self.passenger,
            outbound_flight=self.flight,
            passenger_class='Economy',
            trip_type='OW'
        )
        self.payment = Payment.objects.create(
            amount=Decimal('90.00'),
            booking=self.booking,
            user=self.user
        )

    def test_payment_creation(self):
        self.assertEqual(str(self.payment), f"Payment ID: {self.payment.id}")

    def test_payment_apply_modification_fee(self):
        result = self.payment.apply_modification_fee(Decimal('10.00'))
        self.assertTrue(result)
        self.assertEqual(self.payment.amount, Decimal('80.00'))
        result = self.payment.apply_modification_fee(Decimal('100.00'))
        self.assertFalse(result)
        self.assertEqual(self.payment.amount, Decimal('80.00'))
