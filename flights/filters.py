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
        
class FlightsFilter20(django_filters.FilterSet):
    departure_airport = django_filters.CharFilter(field_name='airportDeparture', label='Departure Airport', lookup_expr='exact', required=True)
    arrival_airport = django_filters.CharFilter(field_name='airportArrival', label='Arrival Airport', lookup_expr='exact', required=True)
    departure_date = django_filters.DateTimeFilter(field_name='departure_date', label='Departure Time', lookup_expr='exact', required=True)
    return_date = django_filters.DateTimeFilter(field_name='departure_date', label='Return Time', method='filter_return_date', required=False)
    ticket_class = django_filters.CharFilter(method='filter_by_class')
    passenger_count = django_filters.NumberFilter(method='filter_by_passenger_count')

    class Meta:
        model = Flight
        fields = ['airportDeparture', 'airportArrival', 'departure_date', 'return_date', 'ticket_class', 'passenger_count']

    def filter_return_date(self, queryset, name, value):
        if value:
            return queryset.filter(departure_date=value)
        return queryset

    def filter_by_class(self, queryset, name, value):
        if value == 'economy':
            return queryset.filter(economy_remaining__gte=self.data.get('passenger_count', 0))
        elif value == 'first':
            return queryset.filter(first_remaining__gte=self.data.get('passenger_count', 0))
        elif value == 'business':
            return queryset.filter(business_remaining__gte=self.data.get('passenger_count', 0))
        return queryset

    def filter_by_passenger_count(self, queryset, name, value):
        ticket_class = self.data.get('ticket_class', '')
        if ticket_class == 'economy':
            return queryset.filter(economy_remaining__gte=value)
        elif ticket_class == 'first':
            return queryset.filter(first_remaining__gte=value)
        elif ticket_class == 'business':
            return queryset.filter(business_remaining__gte=value)
        return queryset

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        if self.data.get('airportDeparture') and self.data.get('airportArrival') and self.data.get('departure_date'):
            departure_airport = self.data.get('airportDeparture')
            arrival_airport = self.data.get('airportArrival')
            departure_date = self.data.get('departure_date')
            return_date = self.data.get('return_date', None)

            flights_outbound = queryset.filter(airportDeparture=departure_airport, airportArrival=arrival_airport, departure_date=departure_date)
            flights_inbound = queryset.filter(airportDeparture=arrival_airport, airportArrival=departure_airport, departure_date=return_date) if return_date else flights_outbound

            combined_flights = flights_outbound | flights_inbound
            return combined_flights
        else:
            return queryset.none()