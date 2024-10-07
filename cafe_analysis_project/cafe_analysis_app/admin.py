from django.contrib import admin
from .models import *
# Register your models here.


class PersonDetectionAdmin(admin.ModelAdmin):
    list_display = ('person_id','time_spent','detection_time','last_seen')

admin.site.register( PersonDetection,PersonDetectionAdmin)


class DetectionSummaryAdmin(admin.ModelAdmin):
    list_display = ('total_persons','updated_at')

admin.site.register(PersonCount,DetectionSummaryAdmin)

class PersonAgeGenderAdmin(admin.ModelAdmin):
    list_display = ('person_detection','age','gender')

admin.site.register(PersonAgeGender,PersonAgeGenderAdmin)

