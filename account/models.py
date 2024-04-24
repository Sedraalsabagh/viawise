from django.db import models
from django.contrib.auth.models import AbstractUser 
from django.conf import settings
# Create your models here.

class User(AbstractUser) :
    

    first_name=models.CharField(max_length=100,blank=True,null=True)
    last_name=models.CharField(max_length=100,blank=True,null=True)
    username=models.EmailField(max_length=254,unique=True,blank=False,null=False)
    created_at=models.DateTimeField(auto_now_add=True)
    is_staff=models.BooleanField(default=False)
    is_superuser=models.BooleanField(default=False)
    is_active=models.BooleanField(default=True)
    password=models.CharField(max_length=128)
    balance=models.DecimalField(max_digits=15, decimal_places=5,null=True)
    #fcm_token = models.CharField(max_length=2000, blank=True, null=True)

    #USERNAME-FIELD=='email',
    def __str__(self):
        return self.username
'''
class Customer(models.Model):
        GUNDER_CHOICES=(
        (1,'male'),
        (2,'female'),
       
    )
        user =models.OneToOneField(User,on_delete=models.CASCADE,primary_key=True)
        phone_number=models.CharField(max_length=20,blank=True,null=True)
        location=models.CharField(max_length=40,blank=True,null=True)
        passport_number=models.CharField(max_length=100,blank=True,null=True)
        gender=models.SmallIntegerField(choices=GUNDER_CHOICES,null=True)
        def __str__(self):
         return str(self.user)
'''
class UserProfile(models.Model):
    GUNDER_CHOICES=(
        (1,'male'),
        (2,'female'),
       
    )
    user=models.OneToOneField(settings.AUTH_USER_MODEL,
    on_delete=models.CASCADE)

    date_of_birth=models.DateField(blank=True,null=True)
    photo=models.ImageField(upload_to='users%Y/%m/%d/',blank=True)
    gender=models.SmallIntegerField(choices=GUNDER_CHOICES,null=True)
    age = models.PositiveSmallIntegerField(blank=True, null=True)
    address=models.CharField(max_length=40,blank=True,null=True)


    def __str__(self):
        return str(self.photo)


