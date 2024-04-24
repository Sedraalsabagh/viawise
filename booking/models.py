from django.db import models
from operator import mod
from account.models import User
from django.dispatch import receiver
from django.utils import timezone
from django.utils.timezone import now
from django.db.models.signals import post_save
from datetime import datetime, timedelta 
from account.models import User
from datetime import timedelta
from decimal import Decimal
from flights.models import Flight#,FlightSeatClass

# Create your models here.


class Passenger(models.Model):
    GENDER_CHOICES = (
        ('Mr','Mr'),
        ('Ms','Ms'),
        ('Mrs','Mrs'),
       )
      
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    gender = models.CharField(max_length=3, choices=GENDER_CHOICES)
    date_of_birth = models.DateField()
    passport_number = models.CharField(max_length=100)
    def __str__(self):
             return f"{self.first_name} {self.last_name}"


class Booking(models.Model):
    STATUS_CHOICES = (
        ('CNL', 'Canceled'),
        ('PPD', 'Postponed'),
        ('CMP', 'Completed'),
    
    )
    TRIP_TYPE_CHOICES = (
        ('OW', 'One Way'),
        ('RT', 'Round Trip'),
    )

    CLASS_CHOICES = (
        ('Economy', 'Economy'),
        ('Business', 'Business'),
        ('First', 'First'),
    ) 
   
   
    user = models.ForeignKey(User, on_delete=models.SET_NULL,null=True)
    Passenger= models.ForeignKey(Passenger, on_delete=models.SET_NULL,null=True)
    outbound_flight = models.ForeignKey(Flight, related_name='outbound_bookings', on_delete=models.SET_NULL, null=True)
    return_flight = models.ForeignKey(Flight, related_name='return_bookings', on_delete=models.SET_NULL, null=True, blank=True)
    booking_date = models.DateTimeField(auto_now_add=True)
    passenger_class = models.CharField(max_length=10, choices=CLASS_CHOICES,null=True)
    trip_type = models.CharField(max_length=10, choices=TRIP_TYPE_CHOICES, default='OW')
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='PPD')
    total_cost=models.DecimalField(max_digits=15, decimal_places=5,null=True)
    def save(self, *args, **kwargs):
        if self.outbound_flight:
            if self.trip_type == 'OW':
                if self.passenger_class == 'Economy' and self.outbound_flight.economy_remaining == 0:
                    raise ValidationError("No economy seats remaining for outbound flight.")
                elif self.passenger_class == 'First' and self.outbound_flight.first_remaining == 0:
                    raise ValidationError("No first class seats remaining for outbound flight.")
                elif self.passenger_class == 'Business' and self.outbound_flight.business_remaining == 0:
                    raise ValidationError("No business class seats remaining for outbound flight.")
            elif self.trip_type == 'RT' and self.return_flight:
                if self.passenger_class == 'Economy' and (self.outbound_flight.economy_remaining == 0 or self.return_flight.economy_remaining == 0):
                    raise ValidationError("No economy seats remaining for outbound or return flight.")
                elif self.passenger_class == 'First' and (self.outbound_flight.first_remaining == 0 or self.return_flight.first_remaining == 0):
                    raise ValidationError("No first class seats remaining for outbound or return flight.")
                elif self.passenger_class == 'Business' and (self.outbound_flight.business_remaining == 0 or self.return_flight.business_remaining == 0):
                    raise ValidationError("No business class seats remaining for outbound or return flight.")

        # Calculate total cost based on seat type and class
        price = self.outbound_flight.price_flight
        if self.passenger_class == 'First':
            price *= Decimal('3')
        elif self.passenger_class == 'Business':
            price *= Decimal('2')
        self.total_cost = price

        super().save(*args, **kwargs)
        if self.outbound_flight:
            if self.trip_type == 'OW':
                if self.passenger_class == 'Economy':
                    self.outbound_flight.economy_remaining -= 1
                elif self.passenger_class == 'First':
                    self.outbound_flight.first_remaining -= 1
                elif self.passenger_class == 'Business':
                    self.outbound_flight.business_remaining -= 1
            elif self.trip_type == 'RT' and self.return_flight:
                if self.passenger_class == 'Economy':
                    self.outbound_flight.economy_remaining -= 1
                    self.return_flight.economy_remaining -= 1
                elif self.passenger_class == 'First':
                    self.outbound_flight.first_remaining -= 1
                    self.return_flight.first_remaining -= 1
                elif self.passenger_class == 'Business':
                    self.outbound_flight.business_remaining -= 1
                    self.return_flight.business_remaining -= 1

            self.outbound_flight.save()
            if self.return_flight:
                self.return_flight.save()
                 



'''  
    
class PushNotificationToken(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE) #we are not using a real User model in this article. You can use the User model specified in your application.
    fcm_token = models.CharField(max_length=200, unique=True)


'''


class Payment(models.Model):
    amount = models.DecimalField(max_digits=15, decimal_places=5,null=True)
    payment_date = models.DateTimeField(auto_now_add=True,null=True)
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE,null=True)
    user=models.ForeignKey(User,on_delete=models.CASCADE,null=True)

    def __str__(self):
        return f"Payment ID: {self.id}"
