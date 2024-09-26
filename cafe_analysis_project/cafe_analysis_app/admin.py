from django.contrib import admin
from .models import *
# Register your models here.
class PersonAdmin(admin.ModelAdmin):
    list_display = ('gender','age_range','first_detected','last_seen')

admin.site.register(Person, PersonAdmin)
