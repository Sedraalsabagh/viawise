from django.test import TestCase
from decimal import Decimal
from datetime import datetime, timedelta
from theaccount.models import User
from flights.models import (
    Policy, Airline, SeatType, Airplane, Flight, Airport, 
    FlightSchedule, RefundedPayment, Review, Offer
)

class PolicyModelTest(TestCase):
    def test_policy_creation(self):
        policy = Policy.objects.create(
            refundable=True,
            exchangeable=True,
            exchangeable_condition="Condition 1",
            cancellation_period=timedelta(days=3)
        )
        self.assertTrue(policy.refundable)
        self.assertTrue(policy.exchangeable)
        self.assertEqual(policy.exchangeable_condition, "Condition 1")
        self.assertEqual(policy.cancellation_period, timedelta(days=3))

class AirlineModelTest(TestCase):
    def setUp(self):
        self.policy = Policy.objects.create(
            refundable=True,
            exchangeable=True,
            exchangeable_condition="Condition 1",
            cancellation_period=timedelta(days=3)
        )

    def test_airline_creation(self):
        airline = Airline.objects.create(
            airline_id=1,
            airline_name="Test Airline",
            description="This is a test airline",
            policy=self.policy
        )
        self.assertEqual(airline.airline_id, 1)
        self.assertEqual(airline.airline_name, "Test Airline")
        self.assertEqual(airline.description, "This is a test airline")
        self.assertEqual(airline.policy, self.policy)

class SeatTypeModelTest(TestCase):
    def test_seat_type_creation(self):
        seat_type = SeatType.objects.create(
            economy_capacity=100,
            business_class_capacity=50,
            first_class_capacity=10,
            economy_weight_limit=30,
            business_class_weight_limit=40,
            first_class_weight_limit=50,
            carry_on_bag_weight_limit=8,
            excess_weight_fee=Decimal('22.00')
        )
        self.assertEqual(seat_type.economy_capacity, 100)
        self.assertEqual(seat_type.business_class_capacity, 50)
        self.assertEqual(seat_type.first_class_capacity, 10)
        self.assertEqual(seat_type.economy_weight_limit, 30)
        self.assertEqual(seat_type.business_class_weight_limit, 40)
        self.assertEqual(seat_type.first_class_weight_limit, 50)
        self.assertEqual(seat_type.carry_on_bag_weight_limit, 8)
        self.assertEqual(seat_type.excess_weight_fee, Decimal('22.00'))
        self.assertEqual(seat_type.economy_price_per_unit, 100)
        self.assertEqual(seat_type.business_class_price_per_unit, 200)
        self.assertEqual(seat_type.first_class_price_per_unit, 300)

class AirplaneModelTest(TestCase):
    def setUp(self):
        self.seat_type = SeatType.objects.create(
            economy_capacity=100,
            business_class_capacity=50,
            first_class_capacity=10
        )
        self.airline = Airline.objects.create(
            airline_id=1,
            airline_name="Test Airline",
            description="This is a test airline",
            policy=Policy.objects.create()
        )

    def test_airplane_creation(self):
        airplane = Airplane.objects.create(
            airplane_name="Boeing 747",
            manufacturer="Boeing",
            manufacturing_date="2020-01-01",
            seats=self.seat_type,
            airline=self.airline
        )
        self.assertEqual(airplane.airplane_name, "Boeing 747")
        self.assertEqual(airplane.manufacturer, "Boeing")
        self.assertEqual(str(airplane.manufacturing_date), "2020-01-01")
        self.assertEqual(airplane.seats, self.seat_type)
        self.assertEqual(airplane.airline, self.airline)

class FlightModelTest(TestCase):
    def setUp(self):
        self.seat_type = SeatType.objects.create(
            economy_capacity=100,
            business_class_capacity=50,
            first_class_capacity=10
        )
        self.airline = Airline.objects.create(
            airline_id=1,
            airline_name="Test Airline",
            description="This is a test airline",
            policy=Policy.objects.create()
        )
        self.airplane = Airplane.objects.create(
            airplane_name="Boeing 747",
            manufacturer="Boeing",
            manufacturing_date="2020-01-01",
            seats=self.seat_type,
            airline=self.airline
        )

    def test_flight_creation(self):
        flight = Flight.objects.create(
            departure_date=datetime.now(),
            Airplane=self.airplane,
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
            price_flight=Decimal('300.00')
        )
        self.assertEqual(flight.Airplane, self.airplane)
        self.assertEqual(flight.airportDeparture, "JFK")
        self.assertEqual(flight.airportArrival, "LAX")
        self.assertEqual(flight.departure_city, "New York")
        self.assertEqual(flight.destination_city, "Los Angeles")
        self.assertEqual(flight.departure_country, "USA")
        self.assertEqual(flight.destination_country, "USA")
        self.assertEqual(flight.economy_remaining, 100)
        self.assertEqual(flight.business_remaining, 50)
        self.assertEqual(flight.first_remaining, 10)
        self.assertEqual(flight.price_flight, Decimal('300.00'))

class AirportModelTest(TestCase):
    def test_airport_creation(self):
        airport = Airport.objects.create(
            airport_name="Los Angeles International Airport",
            IATA_code="LAX",
            contact_info="123-456-7890",
            country="USA",
            comment="This is a comment."
        )
        self.assertEqual(airport.airport_name, "Los Angeles International Airport")
        self.assertEqual(airport.IATA_code, "LAX")
        self.assertEqual(airport.contact_info, "123-456-7890")
        self.assertEqual(airport.country, "USA")
        self.assertEqual(airport.comment, "This is a comment.")

class FlightScheduleModelTest(TestCase):
    def setUp(self):
        self.airport = Airport.objects.create(
            airport_name="Los Angeles International Airport",
            IATA_code="LAX",
            contact_info="123-456-7890",
            country="USA",
            comment="This is a comment."
        )
        self.flight = Flight.objects.create(
            departure_date=datetime.now(),
            Airplane=Airplane.objects.create(
                airplane_name="Boeing 747",
                manufacturer="Boeing",
                manufacturing_date="2020-01-01",
                seats=SeatType.objects.create(economy_capacity=100, business_class_capacity=50, first_class_capacity=10),
                airline=Airline.objects.create(airline_id=1, airline_name="Test Airline", description="This is a test airline", policy=Policy.objects.create())
            ),
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
            price_flight=Decimal('300.00')
        )

    def test_flight_schedule_creation(self):
        flight_schedule = FlightSchedule.objects.create(
            flight=self.flight,
            airport=self.airport,
            duration=timedelta(hours=5),
            comment="This is a comment."
        )
        self.assertEqual(flight_schedule.flight, self.flight)
        self.assertEqual(flight_schedule.airport, self.airport)
        self.assertEqual(flight_schedule.duration, timedelta(hours=5))
        self.assertEqual(flight_schedule.comment, "This is a comment.")

class ReviewModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.flight = Flight.objects.create(
            departure_date=datetime.now(),
            Airplane=Airplane.objects.create(
                airplane_name="Boeing 747",
                manufacturer="Boeing",
                manufacturing_date="2020-01-01",
                seats=SeatType.objects.create(economy_capacity=100, business_class_capacity=50, first_class_capacity=10),
                airline=Airline.objects.create(airline_id=1, airline_name="Test Airline", description="This is a test airline", policy=Policy.objects.create())
            ),
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
            price_flight=Decimal('300.00')
        )

    def test_review_creation(self):
        review = Review.objects.create(
            flight=self.flight,
            user=self.user,
            comment="Great flight!",
            ratings=5
        )
        self.assertEqual(review.flight, self.flight)
        self.assertEqual(review.user, self.user)
        self.assertEqual(review.comment, "Great flight!")
        self.assertEqual(review.ratings, 5)

class OfferModelTest(TestCase):
    def setUp(self):
        self.flight = Flight.objects.create(
            departure_date=datetime.now(),
            Airplane=Airplane.objects.create(
                airplane_name="Boeing 747",
                manufacturer="Boeing",
                manufacturing_date="2020-01-01",
                seats=SeatType.objects.create(economy_capacity=100, business_class_capacity=50, first_class_capacity=10),
                airline=Airline.objects.create(airline_id=1, airline_name="Test Airline", description="This is a test airline", policy=Policy.objects.create())
            ),
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
            price_flight=Decimal('300.00')
        )

    def test_offer_creation(self):
        offer = Offer.objects.create(
            title="Special Discount",
            discount_percentage=Decimal('10.00'),
            start_date=datetime.now().date(),
            end_date=(datetime.now() + timedelta(days=10)).date(),
            description="Limited time offer!",
            conditions="Terms and conditions apply.",
            duration=timedelta(days=10),
            flight=self.flight
        )
        self.assertEqual(offer.title, "Special Discount")
        self.assertEqual(offer.discount_percentage, Decimal('10.00'))
        self.assertEqual(offer.start_date, datetime.now().date())
        self.assertEqual(offer.end_date, (datetime.now() + timedelta(days=10)).date())
        self.assertEqual(offer.description, "Limited time offer!")
        self.assertEqual(offer.conditions, "Terms and conditions apply.")
        self.assertEqual(offer.duration, timedelta(days=10))
        self.assertEqual(offer.flight, self.flight)
