import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta
from theaccount.models import User
from flights.models import Flight, Offer
from .models import AgencyPolicy, Passenger, Booking, Payment

@pytest.fixture
def user(db):
    return User.objects.create(username='testuser', password='password123')

@pytest.fixture
def passenger(db):
    return Passenger.objects.create(
        first_name='John',
        last_name='Doe',
        gender='Mr',
        date_of_birth='1990-01-01',
        passport_number='A12345678'
    )

@pytest.fixture
def flight(db):
    return Flight.objects.create(
        flight_number='XY123',
        departure='2024-06-01 10:00:00',
        arrival='2024-06-01 12:00:00',
        price_flight=Decimal('100.00'),
        economy_remaining=10,
        business_remaining=5,
        first_remaining=2
    )

@pytest.fixture
def booking(db, user, passenger, flight):
    return Booking.objects.create(
        user=user,
        Passenger=passenger,
        outbound_flight=flight,
        passenger_class='Economy',
        trip_type='OW'
    )

@pytest.fixture
def offer(db, flight):
    return Offer.objects.create(
        flight=flight,
        discount_percentage=10,
        start_date=timezone.now() - timedelta(days=1),
        end_date=timezone.now() + timedelta(days=1)
    )

def test_agency_policy_creation(db):
    policy = AgencyPolicy.objects.create(
        policy_type='modify',
        percentage=Decimal('10.00'),
        duration=timedelta(days=3),
        points=100,
        points_offers=50,
        conditions='Some conditions'
    )
    assert policy.__str__() == 'modify policy'

def test_passenger_creation(db):
    passenger = Passenger.objects.create(
        first_name='Jane',
        last_name='Doe',
        gender='Ms',
        date_of_birth='1992-02-02',
        passport_number='B98765432'
    )
    assert passenger.__str__() == 'Jane Doe'

def test_booking_creation(booking):
    assert booking.status == 'PPD'
    assert booking.total_cost == Decimal('100.00')

def test_booking_availability(booking):
    booking.check_availability(booking.outbound_flight, booking.passenger_class)
    with pytest.raises(ValidationError):
        booking.outbound_flight.economy_remaining = 0
        booking.outbound_flight.save()
        booking.check_availability(booking.outbound_flight, booking.passenger_class)

def test_booking_cost_calculation(booking):
    booking.calculate_initial_cost()
    assert booking.total_cost == Decimal('100.00')

def test_booking_apply_discounts(booking, offer):
    booking.apply_discounts()
    assert booking.total_cost == Decimal('90.00')

def test_payment_creation(db, booking, user):
    payment = Payment.objects.create(
        amount=Decimal('90.00'),
        booking=booking,
        user=user
    )
    assert payment.__str__() == f"Payment ID: {payment.id}"

def test_payment_apply_modification_fee(db, booking, user):
    payment = Payment.objects.create(
        amount=Decimal('90.00'),
        booking=booking,
        user=user
    )
    result = payment.apply_modification_fee(Decimal('10.00'))
    assert result is True
    assert payment.amount == Decimal('80.00')
    result = payment.apply_modification_fee(Decimal('100.00'))
    assert result is False
    assert payment.amount == Decimal('80.00')
