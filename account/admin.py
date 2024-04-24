from django.contrib import admin
from . models import User,UserProfile #,Custome,

# Register your models here.


admin.site.register(User)
#admin.site.register(Customer)

@admin.register(UserProfile)
class ProfileAdmin(admin.ModelAdmin):
    list_display=['user','date_of_birth','photo']
    raw_id_fields=['user']
   