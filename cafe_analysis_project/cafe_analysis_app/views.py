from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import threading
from collections import Counter
from .models import *
from django.db.models import Count, Avg, Sum
from django.utils import timezone
from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Count, Sum
from django.db.models.functions import TruncHour
from django.utils import timezone
from .models import PersonAgeGender, PersonDetection, PersonCount

def dashboard_view(request):
    filter_option = request.GET.get('filter', 'current_day')
    today = timezone.now().date()

    # Determine the time range based on the filter
    if filter_option == 'current_day':
        start_date = today
        end_date = today + timezone.timedelta(days=1)
    elif filter_option == 'week':
        start_date = today - timezone.timedelta(weeks=1)
        end_date = today + timezone.timedelta(days=1)
    elif filter_option == 'month':
        start_date = today - timezone.timedelta(days=30)
        end_date = today + timezone.timedelta(days=1)
    elif filter_option == 'year':
        start_date = today - timezone.timedelta(days=365)
        end_date = today + timezone.timedelta(days=1)
    else:
        start_date = today
        end_date = today + timezone.timedelta(days=1)

    # Group data by hour for charts
    age_data = PersonAgeGender.objects.filter(person_detection__detection_time__gte=start_date, person_detection__detection_time__lt=end_date)\
                                      .annotate(hour=TruncHour('person_detection__detection_time'))\
                                      .values('hour', 'age')\
                                      .annotate(count=Count('age'))\
                                      .order_by('hour')

    gender_data = PersonAgeGender.objects.filter(person_detection__detection_time__gte=start_date, person_detection__detection_time__lt=end_date)\
                                         .annotate(hour=TruncHour('person_detection__detection_time'))\
                                         .values('hour', 'gender')\
                                         .annotate(count=Count('gender'))\
                                         .order_by('hour')

    total_time_spent_data = PersonDetection.objects.filter(detection_time__gte=start_date, detection_time__lt=end_date)\
                                                   .annotate(hour=TruncHour('detection_time'))\
                                                   .values('hour')\
                                                   .annotate(total_time_spent=Sum('time_spent'))

    total_persons = PersonCount.objects.filter(date__gte=start_date, date__lt=end_date)\
                                       .annotate(hour=TruncHour('date'))\
                                       .values('hour')\
                                       .annotate(total=Sum('total_persons'))\
                                       .order_by('hour')

    context = {
        'age_data': list(age_data),
        'gender_data': list(gender_data),
        'total_time_spent_data': list(total_time_spent_data),
        'total_persons': list(total_persons),
        'filter_option': filter_option,
    }

    return render(request, 'template/dashboard.html', context)
def get_dashboard_data(request):
    filter_option = request.GET.get('filter', 'current_day')
    today = timezone.now().date()

    # Set date range based on filter
    if filter_option == 'current_day':
        start_date = today
        end_date = today + timezone.timedelta(days=1)
    elif filter_option == 'week':
        start_date = today - timezone.timedelta(weeks=1)
        end_date = today + timezone.timedelta(days=1)
    elif filter_option == 'month':
        start_date = today - timezone.timedelta(days=30)
        end_date = today + timezone.timedelta(days=1)
    elif filter_option == 'year':
        start_date = today - timezone.timedelta(days=365)
        end_date = today + timezone.timedelta(days=1)
    else:
        start_date = today
        end_date = today + timezone.timedelta(days=1)

    # Group by hour
    age_data_qs = PersonAgeGender.objects.filter(person_detection__detection_time__gte=start_date, person_detection__detection_time__lt=end_date)\
                                         .annotate(hour=TruncHour('person_detection__detection_time'))\
                                         .values('hour', 'age')\
                                         .annotate(count=Count('age'))\
                                         .order_by('hour')

    gender_data_qs = PersonAgeGender.objects.filter(person_detection__detection_time__gte=start_date, person_detection__detection_time__lt=end_date)\
                                            .annotate(hour=TruncHour('person_detection__detection_time'))\
                                            .values('hour', 'gender')\
                                            .annotate(count=Count('gender'))\
                                            .order_by('hour')

    total_time_spent_data = PersonDetection.objects.filter(detection_time__gte=start_date, detection_time__lt=end_date)\
                                                   .annotate(hour=TruncHour('detection_time'))\
                                                   .values('hour')\
                                                   .annotate(total_time_spent=Sum('time_spent'))\
                                                   .annotate(avg_time_spent=Avg('time_spent'))\
                                                   .order_by('hour')  # Ensure results are ordered by hour

    total_persons = PersonCount.objects.filter(date__gte=start_date, date__lt=end_date)\
                                       .annotate(hour=TruncHour('date'))\
                                       .values('hour')\
                                       .annotate(total=Sum('total_persons'))\
                                       .order_by('hour')

    # Convert QuerySets to list
    age_data = list(age_data_qs)
    gender_data = list(gender_data_qs)
    total_time_spent = list(total_time_spent_data)
    total_persons = list(total_persons)

    data = {
        'age_data': age_data,
        'gender_data': gender_data,
        'total_time_spent': total_time_spent,
        'total_persons': total_persons,
    }

    return JsonResponse(data)


def get_person_info(request):
    # This is just a placeholder. You should replace this with actual logic to get the latest person data.
    latest_person = PersonDetection.objects.last()  # Assuming you have a way to get the latest detection
    latest_person_age_gender=PersonAgeGender.objects.last()
    if latest_person and latest_person_age_gender:
        data = {
            'person_id': latest_person.person_id,
            'gender': latest_person_age_gender.gender,
            'age': latest_person_age_gender.age,
            'time_spent': latest_person.time_spent,
        }
        return JsonResponse(data)
    return JsonResponse({'error': 'No data available'})




def get_object_info(request):
    # Get the latest object detection
    latest_object = ObjectDetection.objects.last()  # Assuming you have a way to get the latest object detected
    if latest_object:
        data = {
         
            'object_name': latest_object.object_name,
        }
        return JsonResponse(data)
    return JsonResponse({'error': 'No object data available'})