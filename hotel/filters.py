import django_filters
from .models import Hotel 


class HotelFilter(django_filters.FilterSet):
    
    city=django_filters.CharFilter(field_name='city', label='city', lookup_expr='icontains', required=True)
    
    class Meta:
       model =Hotel 
       fields = ['city']
