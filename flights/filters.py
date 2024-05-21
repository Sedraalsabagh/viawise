import django_filters
from .models import Flight,SeatType
from django_filters import FilterSet, CharFilter, DateTimeFilter, ModelChoiceFilter
from django.db.models import F


class FlightsFilter(django_filters.FilterSet):
    
    
    def filter_by_passenger_count(self, queryset, name, value):
        
        return queryset.filter(
            economy_remaining__gte=value if self.data['ticket_class'] == 'Economy' else 0,
            first_remaining__gte=value if self.data['ticket_class'] == 'First' else 0,
            business_remaining__gte=value if self.data['ticket_class'] == 'Business' else 0
        )
    departure_airport = django_filters.CharFilter(field_name='airportDeparture', label='Departure Airport', lookup_expr='exact', required=True)
    arrival_airport = django_filters.CharFilter(field_name='airportArrival', label='Arrival Airport', lookup_expr='exact', required=True)
    departure_date = django_filters.DateTimeFilter(field_name='departure_date', label='Departure Time', lookup_expr='exact', required=True)
    passenger_count = django_filters.NumberFilter(method='filter_by_passenger_count', label='Passenger Count', required=True)
    ticket_class = django_filters.ChoiceFilter(choices=Flight.FLIGHT_SCHEDULE_CHOICES, label='Ticket Class', required=True)
    class Meta:
       model =Flight 
       fields = ['airportDeparture', 'airportArrival','departure_date']

    def filter_queryset(self, queryset):
        if self.data.get('airportDeparture') and self.data.get('airportArrival') and self.data.get('departure_date'):
            if self.data.get('passenger_count') and self.data.get('ticket_class'):
                
                available_tickets = queryset.filter(
                    economy_remaining__gte=self.data['passenger_count'] if self.data['ticket_class'] == 'Economy' else 0,
                    first_remaining__gte=self.data['passenger_count'] if self.data['ticket_class'] == 'First' else 0,
                    business_remaining__gte=self.data['passenger_count'] if self.data['ticket_class'] == 'Business' else 0
                )
                if available_tickets.exists():
                    return super().filter_queryset(available_tickets)
                else:
                    return queryset.none()
            else:
                return super().filter_queryset(queryset)
        else:
            return queryset.none()
        
        


        
class FlightsFilter2(django_filters.FilterSet):
    departure_airport = django_filters.CharFilter(field_name='airportDeparture', label='Departure Airport', lookup_expr='exact', required=True)
    arrival_airport = django_filters.CharFilter(field_name='airportArrival', label='Arrival Airport', lookup_expr='exact', required=True)
    departure_date = django_filters.DateTimeFilter(field_name='departure_date', label='Departure Time', lookup_expr='exact', required=True)

    class Meta:
        model = Flight
        fields = ['airportDeparture', 'airportArrival', 'departure_date']

    def filter_queryset(self, queryset):
        if self.data.get('airportDeparture') and self.data.get('airportArrival') and self.data.get('departure_date'):
            departure = self.data['airportDeparture']
            arrival = self.data['airportArrival']
            date = self.data['departure_date']
            
           
            flights_outbound = queryset.filter(airportDeparture=departure, airportArrival=arrival, departure_date=date)
            
           
            flights_inbound = queryset.filter(airportDeparture=arrival, airportArrival=departure, departure_date=date)
            
           
            combined_flights = flights_outbound | flights_inbound
            
            return combined_flights
        else:
            return queryset.none()  

class FlightsFilter2(django_filters.FilterSet):  #اكتر شي صح بحياتك 
    departure_airport = django_filters.CharFilter(field_name='airportDeparture', label='Departure Airport', lookup_expr='exact', required=True)
    arrival_airport = django_filters.CharFilter(field_name='airportArrival', label='Arrival Airport', lookup_expr='exact', required=True)
    departure_date = django_filters.DateTimeFilter(field_name='departure_date', label='Departure Time', lookup_expr='exact', required=True)
    return_date = django_filters.DateTimeFilter(field_name='departure_date', label='Return Time', method='filter_return_date', required=False)

    class Meta:
        model = Flight
        fields = ['airportDeparture', 'airportArrival', 'departure_date', 'return_date']

    def filter_return_date(self, queryset, name, value):
        if value:
            # Use the return date as the departure date for the return trip
            return queryset.filter(departure_date=value)
        return queryset

    def filter_queryset(self, queryset):
        if self.data.get('airportDeparture') and self.data.get('airportArrival') and self.data.get('departure_date'):
            departure_airport = self.data.get('airportDeparture')
            arrival_airport = self.data.get('airportArrival')
            departure_date = self.data.get('departure_date')
            return_date = self.data.get('return_date', None)

            
            flights_outbound = queryset.filter(airportDeparture=departure_airport, airportArrival=arrival_airport, departure_date=departure_date)

            if return_date:
               
                flights_inbound = queryset.filter(airportDeparture=arrival_airport, airportArrival=departure_airport, departure_date=return_date)
            else:
               
                flights_inbound = queryset.filter(airportDeparture=arrival_airport, airportArrival=departure_airport, departure_date=departure_date)

           
            combined_flights = flights_outbound | flights_inbound
            
            return combined_flights
        else:
            return queryset.none()              
        
class FlightsFilter24(django_filters.FilterSet):
    departure_airport = django_filters.CharFilter(field_name='airportDeparture', label='Departure Airport', lookup_expr='exact', required=True)
    arrival_airport = django_filters.CharFilter(field_name='airportArrival', label='Arrival Airport', lookup_expr='exact', required=True)
    departure_date = django_filters.DateTimeFilter(field_name='departure_date', label='Departure Time', lookup_expr='exact', required=True)
    ticket_class = django_filters.ChoiceFilter(choices=[('economy', 'Economy'), ('business', 'Business'), ('first', 'First Class')], method='filter_by_class')
    passenger_count = django_filters.NumberFilter(label='Passenger Count', method='filter_by_passenger_count', required=True)

    class Meta:
        model = Flight
        fields = ['airportDeparture', 'airportArrival', 'departure_date', 'ticket_class', 'passenger_count']

    def filter_queryset(self, queryset):
        if self.data.get('airportDeparture') and self.data.get('airportArrival') and self.data.get('departure_date'):
            departure = self.data['airportDeparture']
            arrival = self.data['airportArrival']
            date = self.data['departure_date']
            
            # Filter flights departing from departure airport to arrival airport
            flights_outbound = queryset.filter(airportDeparture=departure, airportArrival=arrival, departure_date=date)
            flights_outbound = self.filter_by_class(flights_outbound, 'ticket_class', self.data.get('ticket_class'))
            flights_outbound = self.filter_by_passenger_count(flights_outbound, 'passenger_count', self.data.get('passenger_count'))

            # Filter flights departing from arrival airport to departure airport
            flights_inbound = queryset.filter(airportDeparture=arrival, airportArrival=departure, departure_date=date)
            flights_inbound = self.filter_by_class(flights_inbound, 'ticket_class', self.data.get('ticket_class'))
            flights_inbound = self.filter_by_passenger_count(flights_inbound, 'passenger_count', self.data.get('passenger_count'))

            # Combine the two querysets
            combined_flights = flights_outbound | flights_inbound
            
            return combined_flights
        else:
            return queryset.none()

    def filter_by_class(self, queryset, name, value):
        if value == 'economy':
            return queryset.filter(economy_remaining__gte=self.data.get('passenger_count'))
        elif value == 'business':
            return queryset.filter(business_remaining__gte=self.data.get('passenger_count'))
        elif value == 'first':
            return queryset.filter(first_remaining__gte=self.data.get('passenger_count'))
        return queryset

    def filter_by_passenger_count(self, queryset, name, value):
        # This method's functionality is already applied in filter_by_class
        return queryset        