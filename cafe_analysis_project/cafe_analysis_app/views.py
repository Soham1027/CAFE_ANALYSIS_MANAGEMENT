import json
from django.shortcuts import render
from .forms import *
from .models import *
from django import views
from collections import Counter
# Create your views here.



class DashboardView(views.View):
    def get(self, request, *args, **kwargs):
        persons = Person.objects.all()
        
        # Data preparation for Chart.js
        genders = [person.gender for person in persons if person.gender]  # Only include if gender is not null
        age_ranges = []

        # Categorize the age range
        for person in persons:
            if person.age_range:
                age = int(person.age_range)  # Assuming age_range is a string of the actual age
                if age <= 18:
                    age_ranges.append('0-18')
                elif 18 < age <= 60:
                    age_ranges.append('18-60')
                else:
                    age_ranges.append('60+')

        gender_count = dict(Counter(genders))
        age_range_count = dict(Counter(age_ranges))

        context = {
            'gender_count': json.dumps(gender_count),
            'age_range_count': json.dumps(age_range_count)
        }
        
        return render(request, 'template/dashboard.html', context)