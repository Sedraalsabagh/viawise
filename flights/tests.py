from django.test import TestCase
from django.test import TestCase,Client
from account.models import User
from datetime import datetime, timedelta
from .models import Airplane, SeatType,Policy,Airline,Flight, Airport
# Create your tests here.
from django.test import TestCase
from account.models import User
from datetime import datetime, timedelta
from .models import Airplane, SeatType, Policy, Airline, Flight, Airport

class TestModels(TestCase):
    def test_model_airplane(self):
        seats = SeatType.objects.create(economy_capacity=2, business_class_capacity=3, first_class_capacity=4)
        airplane = Airplane.objects.create(
            airplane_name='Test Item',
            manufacturer='ds',
            manufacturing_date='2003-02-10',
            seattype=seats
        )
        self.assertEqual(str(airplane), 'Test Item')
        self.assertIsInstance(airplane, Airplane)

    def test_flight_model(self):
        policy = Policy.objects.create(refundable=True, exchangeable=True, exchangeable_condition="Test condition", cancellation_period=timedelta(days=1))
        airline = Airline.objects.create(
            airline_name='Test Airline',
            description='Test Description',
            policy=policy
        )
        seat_type = SeatType.objects.create(economy_capacity=100, business_class_capacity=50, first_class_capacity=20)
        departure_airport = Airport.objects.create(
            airport_name='Departure Airport',
            IATA_code='DEP',
            contact_info='Contact Info',
            country='Country'
        )
        destination_airport = Airport.objects.create(
            airport_name='Destination Airport',
            IATA_code='DES',
            contact_info='Contact Info',
            country='Country'
        )
        flight = Flight.objects.create(
            airline=airline,
            airportDeparture=departure_airport,
            airportArrival=destination_airport,
            departure_date=datetime.now().date(),
            return_date=(datetime.now() + timedelta(days=1)).date(),
            duration=timedelta(hours=2),
            notes='Test Notes',
            ratings=4,
        )
        self.assertEqual(flight.airline.airline_name, 'Test Airline')
        self.assertEqual(flight.airportDeparture.airport_name, 'Departure Airport')
        self.assertEqual(flight.airportArrival.airport_name, 'Destination Airport')
        self.assertEqual(flight.departure_date, datetime.now().date())
        self.assertEqual(flight.return_date, (datetime.now() + timedelta(days=1)).date())
        self.assertEqual(flight.duration, timedelta(hours=2))
        self.assertEqual(flight.notes, 'Test Notes')
        self.assertEqual(flight.ratings, 4)



from django.test import TestCase
from .models import Policy, Airline, SeatType

class TestPolicyModel(TestCase):
    def test_policy_str(self):
        policy = Policy.objects.create(
            refundable=True,
            exchangeable=True,
            exchangeable_condition="Test condition",
            cancellation_period=timedelta(days=1)
        )
        self.assertEqual(str(policy), str(policy.id))

class TestAirlineModel(TestCase):
    def test_airline_str(self):
        policy = Policy.objects.create(
            refundable=True,
            exchangeable=True,
            exchangeable_condition="Test condition",
            cancellation_period=timedelta(days=1)
        )
        airline = Airline.objects.create(
            airline_id=1,
            airline_name='Test Airline',
            description='Test Description',
            policy=policy
        )
        self.assertEqual(str(airline), 'Test Airline')

class TestSeatTypeModel(TestCase):
    def test_seat_type_price_calculation(self):
        seat_type = SeatType.objects.create(
            economy_capacity=100,
            business_class_capacity=50,
            first_class_capacity=20
        )
        self.assertEqual(seat_type.economy_price_per_unit, 100)
        self.assertEqual(seat_type.business_class_price_per_unit, 200)
        self.assertEqual(seat_type.first_class_price_per_unit, 300)

