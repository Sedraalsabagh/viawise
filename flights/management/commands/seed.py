from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker
from random import randint
from account.models import User
from django.db import IntegrityError
from ...models import Airline, Airplane, Airport, Flight, FlightSchedule, Policy, RefundedPayment, Review, SeatType
import random
from booking.models import Booking,Passenger,Payment

#عدد البيانات اللي بدي ولدا
NUM_AIRLINES = 20
NUM_AIRPLANES = 20
NUM_AIRPORTS = 20
NUM_FLIGHTS = 20
NUM_FLIGHT_SCHEDULES = 20
NUM_POLICIES = 20
NUM_REFUNDED_PAYMENTS = 20
NUM_REVIEWS = 20
NUM_SEAT_TYPES = 20
NUM_BOOKINGS=20

class Command(BaseCommand):
    help = "Seed the database with dummy data."

    def handle(self, *args, **options):
        self.stdout.write('Seeding data...')

        # إنشاء كائن Faker لتوليد بيانات وهمية
        faker = Faker()

        # توليد بيانات للسياسات
        self.stdout.write('Seeding Policies...')
        for _ in range(NUM_POLICIES):
            policy = Policy.objects.create(
                refundable=faker.boolean(),
                exchangeable=faker.boolean(),
                exchangeable_condition=faker.text(max_nb_chars=255),
                cancellation_period=timezone.timedelta(days=randint(0, 30))
            )

        #   للشركات
        self.stdout.write('Seeding Airlines...')
        for _ in range(NUM_AIRLINES):
             airline, _ = Airline.objects.get_or_create(
              airline_id=randint(1000, 9999),
              airline_name=faker.company(),
              description=faker.text(max_nb_chars=400),
              defaults={'policy': Policy.objects.get_or_create(
                  refundable=faker.boolean(),
                  exchangeable=faker.boolean(),
                  exchangeable_condition=faker.text(max_nb_chars=255),
                  cancellation_period=timezone.timedelta(days=randint(0, 30))
              )[0]}
            )
             if not Airline.objects.filter(airline_id=airline.airline_id).exists():
                airline.save()
        #   لأنواع المقاعد
        self.stdout.write('Seeding SeatTypes...')
        existing_first_class_capacities = set()

        for _ in range(NUM_SEAT_TYPES):
                first_class_capacity = randint(5, 20)
                try:
                 seat_type = SeatType.objects.create(

                  economy_capacity=randint(50, 300),
                  business_class_capacity=randint(10, 50),
                  first_class_capacity=first_class_capacity,
                  economy_weight_limit=randint(20, 40),
                  business_class_weight_limit=randint(30, 50),
                  first_class_weight_limit=randint(40, 60),
                  carry_on_bag_weight_limit=8,
                  excess_weight_fee=22
            )
                except IntegrityError:
                 # إذا كانت القيمة مكررة، قم بالتعامل مع الخطأ هنا
                 print(f"Skipping duplicate first_class_capacity: {first_class_capacity}")



        #   للطائرات
        self.stdout.write('Seeding Airplanes...')
        for _ in range(NUM_AIRPLANES):
            airplane = Airplane(
                airplane_name=faker.word(),
                manufacturer=faker.company(),
                manufacturing_date=faker.date_between(start_date='-30y', end_date='today'),
                seats=SeatType.objects.get_or_create(pk=random.randint(1, NUM_SEAT_TYPES))[0],
                airline=random.choice(Airline.objects.all())
            )
            if not Airplane.objects.filter(airplane_name=airplane.airplane_name).exists():
                airplane.save()




        #   للمطارات
        self.stdout.write('Seeding Airports...')
        for _ in range(NUM_AIRPORTS):
            airport = Airport.objects.create(
                airport_name=faker.word(),
                IATA_code=faker.lexify(text='???'),
                contact_info=faker.text(),
                country=faker.country()
            )

        #   للرحلات
        self.stdout.write('Seeding Flights...')
        for _ in range(NUM_FLIGHTS):
            flight = Flight.objects.create(
                departure_date=faker.date_time_this_decade(),
                Airplane=random.choice(Airplane.objects.all()), 
                return_date=faker.date_time_this_decade(),
                duration=timezone.timedelta(hours=randint(1, 12)),
                airportDeparture=random.choice(Airport.objects.all()),
                airportArrival=random.choice(Airport.objects.all()),
                notes=faker.text(max_nb_chars=200),
                ratings=randint(1, 5),
                departure_city=faker.city(),
                destination_city=faker.city(),
                departure_country=faker.country(),
                destination_country=faker.country(),
                economy_remaining=randint(0, 200),
                first_remaining=randint(0, 50),
                business_remaining=randint(0, 30),
                price_flight=randint(100, 1000)
            )


        

        #   للتقييمات
        self.stdout.write('Seeding Reviews...')
        for _ in range(NUM_REVIEWS):
            review = Review.objects.create(
                flight=random.choice(Flight.objects.all()),
                user=random.choice(User.objects.all()),
                comment=faker.text(max_nb_chars=2000),
                ratings=randint(1, 5)
            )

        self.stdout.write(self.style.SUCCESS('Data seeding complete.'))



        

        self.stdout.write('Seeding Bookings...')
        self.stdout.write('Seeding Bookings...')
        for _ in range(NUM_BOOKINGS):
            user = User.objects.order_by('?').first()
            passenger = Passenger.objects.create(
                first_name=faker.first_name(),
                last_name=faker.last_name(),
                gender=faker.random_element(elements=('Mr', 'Ms', 'Mrs')),
                date_of_birth=faker.date_of_birth(),
                passport_number=faker.lexify(text='??######')
            )
            flight = Flight.objects.order_by('?').first()
            Booking.objects.create(
                user=user,
                Passenger=passenger,
                outbound_flight=flight,
                booking_date=faker.date_time_between(start_date='-30d', end_date='now'),
                passenger_class=faker.random_element(elements=('Economy', 'Business', 'First')),
                trip_type=faker.random_element(elements=('OW', 'RT')),
                status=faker.random_element(elements=('CNL', 'PPD', 'CMP')),
                total_cost=faker.pydecimal(left_digits=4, right_digits=2, positive=True)
            )

        self.stdout.write(self.style.SUCCESS('Data seeding complete.'))