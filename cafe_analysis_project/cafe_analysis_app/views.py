from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import threading
# from .process_video import process_live_video_with_stop
from collections import Counter
from .models import *
from django.db.models import Count,Avg,Sum
from django.utils import timezone
from datetime import timedelta

# @csrf_exempt
# def start_video_processing(request):
#     # Replace with the actual IP address and port of your DroidCam server
#     stream_url = 'http://192.168.29.113:4747/video'
    
#     # Start processing video in a separate thread
#     video_thread = threading.Thread(target=process_live_video, args=(stream_url,))
#     video_thread.start()
#     return HttpResponse("Live video processing started")



def dashboard_view(request):
    filter_option = request.GET.get('filter', 'day')  # Default to 'day'
    today = timezone.now().date()

    # Calculate start_date and end_date for filtering
    if filter_option == 'current_day':
        start_date = today
        end_date = today + timezone.timedelta(days=1)  # Next day, exclusive
    # elif filter_option == 'yesterday':
    #     start_date = today - timezone.timedelta(days=1)
    #     end_date = today  # Until the end of yesterday
    elif filter_option == 'week':
        start_date = today - timezone.timedelta(weeks=1)
        end_date = today + timezone.timedelta(days=1)  # Up to the end of today
    elif filter_option == 'month':
        start_date = today - timezone.timedelta(days=30)
        end_date = today + timezone.timedelta(days=1)  # Up to the end of today
    elif filter_option == 'year':
        start_date = today - timezone.timedelta(days=365)
         # Up to the end of today
    else:
        start_date = today
        end_date = today + timezone.timedelta(days=1)  # Next day, exclusive

    # Adjust queryset filters
    age_data = PersonDetection.objects.filter(detection_time__date__gte=start_date, detection_time__date__lt=end_date).values('age').annotate(count=Count('age')).order_by('age')
    gender_data = PersonDetection.objects.filter(detection_time__date__gte=start_date, detection_time__date__lt=end_date).values('gender').annotate(count=Count('gender')).order_by('gender')
    avg_time_spent_data = PersonDetection.objects.filter(detection_time__date__gte=start_date, detection_time__date__lt=end_date).aggregate(avg_time_spent=Avg('time_spent'))
    
    total_persons = PersonCount.objects.filter(date__date__gte=start_date, date__date__lt=end_date).aggregate(total=Sum('total_persons'))['total'] or 0 

    context = {
        'age_data': age_data,
        'gender_data': gender_data,
        'avg_time_spent': avg_time_spent_data['avg_time_spent'] or 0,
        'total_persons': total_persons,
        'filter_option': filter_option,
    }

    return render(request, 'template/dashboard.html', context)

def get_dashboard_data(request):
    filter_option = request.GET.get('filter', 'day')
    today = timezone.now().date()

    if filter_option == 'current_day':
        start_date = today
    # elif filter_option == 'yesterday':
    #     start_date = today - timezone.timedelta(days=1)
    elif filter_option == 'week':
        start_date = today - timezone.timedelta(weeks=1)
    elif filter_option == 'month':
        start_date = today - timezone.timedelta(days=30)
    elif filter_option == 'year':
        start_date = today - timezone.timedelta(days=365)
    else:
        start_date = today

    # Querysets
    age_data_qs = PersonDetection.objects.filter(detection_time__date__gte=start_date).values('age').annotate(count=Count('age')).order_by('age')
    gender_data_qs = PersonDetection.objects.filter(detection_time__date__gte=start_date).values('gender').annotate(count=Count('gender')).order_by('gender')
    avg_time_spent = PersonDetection.objects.filter(detection_time__date__gte=start_date).aggregate(avg_time_spent=Avg('time_spent'))['avg_time_spent'] or 0
    total_persons = PersonCount.objects.filter(date__date__gte=start_date).aggregate(total=Sum('total_persons'))['total'] or 0 

    # Convert QuerySets to list
    age_data = list(age_data_qs)
    gender_data = list(gender_data_qs)

    # Prepare the data for JSON response
    data = {
        'age_data': age_data,
        'gender_data': gender_data,
        'avg_time_spent': avg_time_spent,
        'total_persons': total_persons,
    }

    return JsonResponse(data)