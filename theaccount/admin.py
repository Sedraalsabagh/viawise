from django.contrib import admin
from . models import User,UserProfile ,Contact #PointBalance




admin.site.register(User)
admin.site.register(Contact)
#admin.site.register(UserProfile)
#admin.site.register(PointBalance)


@admin.register(UserProfile)
class ProfileAdmin(admin.ModelAdmin):
    list_display=['user','age','photo']
    raw_id_fields=['user']
   