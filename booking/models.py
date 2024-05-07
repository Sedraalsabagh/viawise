from django.db import models
from operator import mod
from django.dispatch import receiver
from django.utils import timezone
from django.utils.timezone import now
from django.db.models.signals import post_save
from datetime import datetime, timedelta 
from account.models import User
from datetime import timedelta
from decimal import Decimal
from flights.models import *
from django.core.exceptions import ValidationError

# Create your models here.

class PolicyAgency(models.Model):
    
    modifiable = models.BooleanField()  
    modify_period = models.DurationField(default=timedelta(days=0))  
    cancellable = models.BooleanField()  
    cancel_period = models.DurationField(default=timedelta(days=0))  
    cancel_without_payment = models.DurationField(default=timedelta(days=0)) 
    cancellation_discount_amount = models.DecimalField(max_digits=15, decimal_places=5, default=1)


class AgencyPolicy(models.Model):
    
    
    POLICY_CHOICES = (
        ('modify', 'Modify'),  
        ('cancel', 'Cancel'),  
        ('offers', 'Offers'),  
        ('cancel_without_payment', 'Cancel Without Payment') ,
        ('cancel_over_week', 'cancel_over_week') 
    )
    DEFAULT_POLICY_TYPE = 'default_policy'
    policy_type = models.CharField(max_length=100, choices=POLICY_CHOICES,default=DEFAULT_POLICY_TYPE)  
    percentage = models.DecimalField(max_digits=5, decimal_places=2,null=True)  
    duration = models.DurationField(default=timedelta(days=0)) 
    points = models.PositiveIntegerField(default=0) 
    points_offers= models.PositiveIntegerField(default=0) 

    def __str__(self):
        return f"{self.policy_type} policy"


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
    creation_time = models.DateTimeField(default=timezone.now)
    def save(self, *args, **kwargs):
        if not self.pk:  
            self.validate_availability()
            self.calculate_initial_cost()
            self.apply_discounts()
            self.update_seat_count()
        
        super().save(*args, **kwargs)

    def validate_availability(self):
        
        if self.outbound_flight:
            if self.trip_type == 'OW':
                self.check_availability(self.outbound_flight, self.passenger_class)
            elif self.trip_type == 'RT' and self.return_flight:
                self.check_availability(self.outbound_flight, self.passenger_class)
                self.check_availability(self.return_flight, self.passenger_class)

    def check_availability(self, flight, passenger_class):
        remaining_seats = getattr(flight, f"{passenger_class.lower()}_remaining")
        if remaining_seats == 0:
            raise ValidationError(f"No {passenger_class.lower()} class seats remaining for flight {flight.id}.")

    def calculate_initial_cost(self):
        
        if self.outbound_flight:
            price = self.outbound_flight.price_flight
            multiplier = Decimal('3') if self.passenger_class == 'First' else Decimal('2') if self.passenger_class == 'Business' else Decimal('1')
            self.total_cost = price * multiplier

    def apply_discounts(self):
        
        if self.trip_type == 'RT' and self.return_flight:
            self.total_cost = self.calculate_discount(self.outbound_flight, self.total_cost)
            self.total_cost += self.calculate_discount(self.return_flight, self.return_flight.price_flight)
        elif self.outbound_flight:
            self.total_cost = self.calculate_discount(self.outbound_flight, self.total_cost)

    def calculate_discount(self, flight, price):
        offers = Offer.objects.filter(flight=flight, start_date__lte=datetime.now(), end_date__gte=datetime.now())
        if offers.exists():
            max_discount = max(offer.discount_percentage for offer in offers)
            discount_amount = price * Decimal(max_discount) / Decimal(100)
            return price - discount_amount
        return price

    def update_seat_count(self):
        
        if self.outbound_flight:
            if self.trip_type == 'OW':
                self.decrement_seat_count(self.outbound_flight, self.passenger_class)
            elif self.trip_type == 'RT' and self.return_flight:
                self.decrement_seat_count(self.outbound_flight, self.passenger_class)
                self.decrement_seat_count(self.return_flight, self.passenger_class)
            self.outbound_flight.save()
            if self.return_flight:
                self.return_flight.save()

    def decrement_seat_count(self, flight, passenger_class):
        attr = f"{passenger_class.lower()}_remaining"
        current_remaining = getattr(flight, attr)
        setattr(flight, attr, current_remaining - 1)
                 



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
