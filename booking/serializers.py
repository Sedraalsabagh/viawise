from rest_framework import serializers
from .models import Booking,Passenger,Payment#,PushNotificationToken
from flights.models import Flight,Airline#,FlightSeatClass



class PassengerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Passenger
        fields = '__all__'


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields =['user','Passenger','outbound_flight','return_flight','trip_type','passenger_class']


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'  
        
        
class FlightSerializer1(serializers.ModelSerializer):
    class Meta:
        model = Flight
        fields = ['airportDeparture','airportArrival']

class BookingSerializer1(serializers.ModelSerializer):
    outbound_flight = FlightSerializer1()

    class Meta:
        model = Booking
        fields = ['user', 'Passenger', 'outbound_flight', 'return_flight', 'trip_type', 'passenger_class','total_cost','booking_date']        
        
class AirlineSerializer2(serializers.ModelSerializer):
    class Meta:
        model = Airline
        fields = ['airline_name']

class FlightSerializer2(serializers.ModelSerializer):
    airline = AirlineSerializer2()  # تضمين معلومات الشركة الجوية

    class Meta:
        model = Flight
        fields = ['airportDeparture', 'airportArrival','airline']  # تضمين معلومات الشركة الجوية

class BookingSerializer2(serializers.ModelSerializer):
    outbound_flight = FlightSerializer2()

    class Meta:
        model = Booking
        fields = ['user', 'Passenger', 'outbound_flight', 'return_flight', 'trip_type', 'passenger_class', 'total_cost', 'booking_date']
class FlightSerializer3(serializers.ModelSerializer):
    airline_name = serializers.CharField(source='airplane.airline.airline_name')

    class Meta:
        model = Flight
        fields = ['airportDeparture', 'airportArrival', 'airline_name']

class BookingSerializer3(serializers.ModelSerializer):
    outbound_flight = FlightSerializer3()

    class Meta:
        model = Booking
        fields = ['user', 'Passenger', 'outbound_flight', 'return_flight', 'trip_type', 'passenger_class', 'total_cost', 'booking_date','status']


'''
class PushNotificationTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = PushNotificationToken
        fields = '__all__'
'''
'''
    def validate(self, data):
     outbound_flight = data.get('outbound_flight')
     return_flight = data.get('return_flight')

     if outbound_flight == return_flight:
        raise serializers.ValidationError("Outbound and return flights cannot be the same")

     passengers_data = data.get('passengers', [])
     passenger_names = [passenger.get('name') for passenger in passengers_data]
     if len(passenger_names) != len(set(passenger_names)):
        raise serializers.ValidationError("Passenger names must be unique within a booking")

     passport_numbers = [passenger.get('passport_number') for passenger in passengers_data]
     if len(passport_numbers) != len(set(passport_numbers)):
        raise serializers.ValidationError("Passport numbers must be unique within a booking")
    # if not outbound_flight.flightseatclass_set.filter(id=seat_class_id).exists():
     #       raise serializers.ValidationError("Selected seat class is not available for the outbound flight")

     return data
'''

   # def create(self, validated_data):
    #    passengers_data = validated_data.pop('passengers', [])
     #   booking = Booking.objects.create(**validated_data)
    #    for passenger_data in passengers_data:
     #       Passenger.objects.create(booking=booking, **passenger_data)
      #s  return booking
      
      
      #git 
      #sedra #qq







