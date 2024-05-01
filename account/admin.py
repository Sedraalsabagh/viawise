from django.contrib import admin
from . models import User,UserProfile ,PointBalance




admin.site.register(User)

admin.site.register(PointBalance)


@admin.register(UserProfile)
class ProfileAdmin(admin.ModelAdmin):
    list_display=['user','age','photo']
    raw_id_fields=['user']
   