from rest_framework import serializers
from .models import Hotel

class HotelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hotel
        fields = '__all__' 
        
        
        
class HotelSerializer1(serializers.ModelSerializer):
    class Meta:
        model = Hotel
        fields = ['name']        