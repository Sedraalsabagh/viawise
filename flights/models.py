from django.db import models
from datetime import datetime, timedelta
from theaccount.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

     
class Policy(models.Model):
    refundable = models.BooleanField(default=False)
    exchangeable = models.BooleanField(default=False)
    exchangeable_condition = models.CharField(max_length=255, blank=True, null=True)
    cancellation_period = models.DurationField(default=timedelta(days=0))

    def __str__(self):
        return str(self.id)

class Airline(models.Model):
    airline_id = models.IntegerField(default=0, blank=False)
    airline_name = models.CharField(max_length=100)
    description = models.TextField(max_length=400)
    policy = models.ForeignKey(Policy, on_delete=models.CASCADE)


    def __str__(self):
        return self.airline_name

class SeatType(models.Model):
    economy_capacity = models.IntegerField(null=True, blank=False, unique=True)
    business_class_capacity = models.IntegerField(null=True, blank=False, unique=True)
    first_class_capacity = models.IntegerField(null=True, blank=False, unique=True)
    economy_weight_limit = models.IntegerField(default=30, null=True, blank=False)
    business_class_weight_limit = models.IntegerField(default=40, null=True, blank=False)
    first_class_weight_limit = models.IntegerField(default=50, null=True, blank=False)
    carry_on_bag_weight_limit = models.IntegerField(default=8, null=True, blank=False)
    excess_weight_fee = models.DecimalField(max_digits=10, decimal_places=2, default=22)
    @property
    def economy_price_per_unit(self):
        price = 100  
        return price

    @property
    def business_class_price_per_unit(self):
        price = 100  
        return price * 2  

    @property
    def first_class_price_per_unit(self):
        price = 100  
        return price * 3  
    

    def __str__(self):
        return str(self.id)

    
class Airplane(models.Model):
    
    airplane_name = models.CharField(max_length=100)
    manufacturer = models.CharField(max_length=100)
    manufacturing_date = models.DateField()
    seats= models.ForeignKey(SeatType, on_delete=models.CASCADE)  
    airline=models.ForeignKey(Airline, on_delete=models.CASCADE,null=True)

    
   


class Flight(models.Model):
     
   
    DESTINATION_ACTIVITY = (
        ('Sightseeing', 'Sightseeing'),  
        ('Skiing', 'Skiing'),  
        ('Beach relaxation', 'Beach relaxation'),  
        
    )
    DESTIATION_CHOICES = (
        ('Business', 'Business'),  
        ('Tourism', 'Tourism'),  
        ('Education', 'Education'),  
        ('Entertainment', 'Entertainment')  
    )
    CLIMATE_CHOICES = (
        ('Warm', 'Warm'),  
        ('Cold', 'Cold'),  
        ('Moderate', 'Moderate'),  
    )
    FLIGHT_SCHEDULE_CHOICES = (
        ('Direct', 'Direct'),
        ('Transit', 'Transit'),
    )
    departure_date=models.DateField(default=datetime.now)
   # airline=models.ForeignKey(Airline, on_delete=models.CASCADE,default=1)
    Airplane=models.ForeignKey(Airplane, on_delete=models.CASCADE,default=1)
    
    duration =models.DurationField(default=timedelta(days=0))
    airportDeparture=models.CharField(max_length=40,blank=False,null=False)
    airportArrival=models.CharField(max_length=40,blank=False,null=False)
    notes=models.TextField(max_length=200,blank=True,null=True)
    ratings=models.IntegerField(blank=True, null=True)
    
    departure_city = models.CharField(max_length=100,null=True,default='')
    destination_city = models.CharField(max_length=100,blank=False,null=False,default='')
    departure_country = models.CharField(max_length=100,blank=False,null=False,default='')
    destination_country = models.CharField(max_length=100,blank=False,null=False,default='')
    economy_remaining =models.IntegerField(default=20,null=True)
    first_remaining = models.IntegerField(default=10,null=True)
    business_remaining = models.IntegerField(default=10,null=True)
    price_flight= models.DecimalField(default=10.1, max_digits=10, decimal_places=2)

    destination_activity = models.CharField(max_length=100, choices=DESTINATION_ACTIVITY,blank=True, null=True)
    destination_type=models.CharField(max_length=100,choices=DESTIATION_CHOICES,blank=True, null=True)
    destination_climate = models.CharField(max_length=100,choices=CLIMATE_CHOICES, blank=True, null=True)
    flight_schedule = models.CharField(max_length=100, choices=FLIGHT_SCHEDULE_CHOICES, blank=True, null=True)

    description = models.TextField(max_length=2000, default="", blank=True,null=True)

    def __str__(self): 
        return str(self.id)

'''
    activities = models.TextField(blank=True, null=True)
    temperature = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    rainfall = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
'''
    


class Airport(models.Model):
    airport_id = models.AutoField(primary_key=True)
    airport_name = models.CharField(max_length=100)
    IATA_code = models.CharField(max_length=3)
    contact_info = models.TextField()
    country = models.CharField(max_length=50)
    comment = models.TextField(max_length=2000, default="", blank=False)

    def __str__(self):     
        return self.airport_name

class FlightSchedule(models.Model):
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE)
    airport = models.ForeignKey(Airport, on_delete=models.CASCADE)
    duration = models.DurationField()
    comment = models.TextField(max_length=2000, default="", blank=False)



    def __str__(self):
        return f"{self.flight} - {self.airport}"

class RefundedPayment(models.Model):
    #booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    notes = models.TextField()

   # def __str__(self):
      #  return f"Refund for booking {self.booking.booking_id} - Amount: {self.amount}"



class Review(models.Model):
    flight = models.ForeignKey(Flight, null=True, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    comment = models.TextField(max_length=2000, default="", blank=False)
    ratings = models.IntegerField(default=0)
    createAt = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.ratings)

class Offer(models.Model):
    title = models.CharField(max_length=200, null=True, blank=True)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField()
    description = models.TextField(blank=True, null=True)
    conditions = models.TextField(blank=True, null=True)
    duration= models.DurationField(default=timedelta(days=0))  
    flight=models.ForeignKey(Flight,on_delete=models.CASCADE,null=True)