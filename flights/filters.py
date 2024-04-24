import django_filters
from .models import Flight,SeatType
from django_filters import FilterSet, CharFilter, DateTimeFilter, ModelChoiceFilter


class FlightsFilter(django_filters.FilterSet):
    departure_airport = django_filters.CharFilter(field_name='airportDeparture', label='Departure Airport', lookup_expr='exact', required=True)
    arrival_airport = django_filters.CharFilter(field_name='airportArrival', label='Arrival Airport', lookup_expr='exact', required=True)
    departure_date = django_filters.DateTimeFilter(field_name='departure_date', label='Departure Time', lookup_expr='exact', required=True)
    return_date = django_filters.DateTimeFilter(field_name='departure_date', label='Return Time', lookup_expr='exact', required=True)
    departure_city= django_filters.CharFilter(field_name='departure_city', label='departure_city', lookup_expr='exact', required=True)
    destination_city= django_filters.CharFilter(field_name='destination_city', label='destination_city', lookup_expr='exact', required=True)
    departure_country=django_filters.CharFilter(field_name='departure_country', label='departure_country', lookup_expr='exact', required=True)
    destination_country=django_filters.CharFilter(field_name='destination_country', label='destination_country', lookup_expr='exact', required=True)
    
    class Meta:
       model =Flight
       fields = ['airportDeparture', 'airportArrival','departure_date','return_date','departure_city','destination_city','departure_country','destination_country']

    def filter_queryset(self, queryset):
        if self.data.get('airportDeparture') or self.data.get('departure_city') or self.data.get('departure_country')  and self.data.get('airportArrival') or self.data.get('destination_city') or self.data.get('destination_country')  and self.data.get('departure_date')  and self.data.get('return_date') :
            return super().filter_queryset(queryset)
        else:
            return queryset.none() #sed