
'''
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User
from .models import Booking

@receiver(post_save, sender=Booking)
def send_booking_reminder(sender, instance, created, **kwargs):
    if created:  # يتم إرسال الإشعار فقط عند إنشاء الحجز
        outbound_flight_date = instance.outbound_flight.departure_date

        # تاريخ ووقت الإشعار (24 ساعة قبل موعد اقلاع الرحلة)
        reminder_datetime = outbound_flight_date - timedelta(hours=24)

        # إذا كان تاريخ ووقت الإشعار قد حان، فأرسل الإشعار
        if timezone.now() >= reminder_datetime:
            notify.send(instance.user, 
                        verb=f"Your flight is coming up on {outbound_flight_date}. Don't forget to prepare!")



'''
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Booking
from flights.models import Flight
#from . import notification  # استيراد وظيفة الإشعار
'''
@receiver(post_save, sender=Booking)
def send_reminder_notification(sender, instance, created, **kwargs):
    if created:  # التأكد من أن هذا الحجز هو حجز جديد
        # حساب الوقت قبل الموعد المحدد (24 ساعة)
        reminder_time = instance.outbound_flight.departure_date - timezone.timedelta(hours=24)
        # التحقق مما إذا كان الوقت الحالي يقع قبل وقت الإشعار
        if timezone.now() < reminder_time:
            # إرسال الإشعار باستخدام رمز FCM المتوفر
            fcm_token = instance.user.pushnotificationtoken.fcm_token
            trip_name = f"{instance.outbound_flight.departure_city} إلى {instance.outbound_flight.destination_city}"
            notification.send_push_notification(fcm_token, trip_name)
'''