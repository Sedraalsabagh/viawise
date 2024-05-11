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
    def filter_by_passenger_count(self, queryset, name, value):
        return queryset.filter(
            economy_remaining__gte=value if self.data['ticket_class'] == 'Economy' else 0,
            first_remaining__gte=value if self.data['ticket_class'] == 'First' else 0,
            business_remaining__gte=value if self.data['ticket_class'] == 'Business' else 0
        )

    departure_airport = django_filters.CharFilter(field_name='airportDeparture', label='Departure Airport', lookup_expr='exact', required=True)
    arrival_airport = django_filters.CharFilter(field_name='airportArrival', label='Arrival Airport', lookup_expr='exact', required=True)
    departure_date = django_filters.DateTimeFilter(field_name='departure_date', label='Departure Time', lookup_expr='exact', required=True)
    return_datee = django_filters.DateTimeFilter(field_name='return_datee', label='Return Time', lookup_expr='exact', required=False)
    passenger_count = django_filters.NumberFilter(method='filter_by_passenger_count', label='Passenger Count', required=True)
    ticket_class = django_filters.ChoiceFilter(choices=Flight.FLIGHT_SCHEDULE_CHOICES, label='Ticket Class', required=True)

    class Meta:
       model = Flight
       fields = ['airportDeparture', 'airportArrival', 'departure_date', 'return_datee']

    def filter_queryset(self, queryset):
        if self.data.get('airportDeparture') and self.data.get('airportArrival') and self.data.get('departure_date') and self.data.get('return_datee'):
            if self.data.get('passenger_count') and self.data.get('ticket_class'):
             
                arrival_airport, departure_airport = self.data['airportDeparture'], self.data['airportArrival']
              
                return_date = self.data['return_datee'] if self.data['return_datee'] else self.data['departure_date']
               
                available_tickets = queryset.filter(
                    airportDeparture=arrival_airport,
                    airportArrival=departure_airport,
                    departure_date=return_date,
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
        
import django_filters

class RoundTripFilter(django_filters.FilterSet):
    departure_airport = django_filters.CharFilter(field_name='airportDeparture', lookup_expr='exact')
    arrival_airport = django_filters.CharFilter(field_name='airportArrival', lookup_expr='exact')
    departure_date = django_filters.DateTimeFilter(field_name='departure_date', lookup_expr='exact')
    return_date = django_filters.DateTimeFilter(field_name='return_date', lookup_expr='exact', method='filter_return_date')
    round_trip = django_filters.BooleanFilter(method='filter_round_trip')

    class Meta:
        model = Flight
        fields = ['departure_airport', 'arrival_airport', 'departure_date', 'return_date']

    def filter_return_date(self, queryset, name, value):
        return queryset.annotate(departure_datetime=F('departure_date')).filter(departure_datetime=value)

    def filter_round_trip(self, queryset, name, value):
        if value:
            departure_airport = self.data.get('departure_airport')
            arrival_airport = self.data.get('arrival_airport')
            departure_date = self.data.get('departure_date')
            return_date = self.data.get('return_date')

            return queryset.filter(
                Q(airportDeparture=departure_airport, airportArrival=arrival_airport, departure_date=departure_date) |
                Q(airportDeparture=arrival_airport, airportArrival=departure_airport, departure_date=return_date)
            )
        else:
            return queryset