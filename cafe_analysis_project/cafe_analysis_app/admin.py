from django.contrib import admin
from .models import *
# Register your models here.


class PersonDetectionAdmin(admin.ModelAdmin):
    list_display = ('person_id','age','gender','time_spent','detection_time','last_seen')

admin.site.register( PersonDetection,PersonDetectionAdmin)


class DetectionSummaryAdmin(admin.ModelAdmin):
    list_display = ('total_persons','updated_at','date')

admin.site.register(PersonCount,DetectionSummaryAdmin)

