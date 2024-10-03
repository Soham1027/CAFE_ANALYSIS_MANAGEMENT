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
    
    if filter_option == 'current_day':
        start_date = today
    elif filter_option == 'yesterday':
        start_date = today - timezone.timedelta(days=1)
    elif filter_option == 'week':
        start_date = today - timezone.timedelta(weeks=1)
    elif filter_option == 'month':
        start_date = today - timezone.timedelta(days=30)
    elif filter_option == 'year':
        start_date = today - timezone.timedelta(days=365)
    else:
        start_date = today

    age_data = PersonDetection.objects.filter(detection_time__date=start_date).values('age').annotate(count=Count('age')).order_by('age') or 0
    gender_data = PersonDetection.objects.filter(detection_time__date=start_date).values('gender').annotate(count=Count('gender')).order_by('gender') or 0
    avg_time_spent_data = PersonDetection.objects.filter(detection_time__date=start_date).aggregate(avg_time_spent=Avg('time_spent')) or 0
    
    # Adjusted total_persons calculation
    total_persons = PersonCount.objects.filter(date__date=start_date).aggregate(total=Sum('total_persons'))['total'] or 0 

    context = {
        'age_data': age_data,
        'gender_data': gender_data,
        'avg_time_spent': avg_time_spent_data['avg_time_spent'],
        'total_persons': total_persons,
        'filter_option': filter_option,
    }

    return render(request, 'template/dashboard.html', context)

def get_dashboard_data(request):
    filter_option = request.GET.get('filter', 'day')
    today = timezone.now().date()

    if filter_option == 'current_day':
        start_date = today
    elif filter_option == 'yesterday':
        start_date = today - timezone.timedelta(days=1)
    elif filter_option == 'week':
        start_date = today - timezone.timedelta(weeks=1)
    elif filter_option == 'month':
        start_date = today - timezone.timedelta(days=30)
    elif filter_option == 'year':
        start_date = today - timezone.timedelta(days=365)
    else:
        start_date = today

    age_data = PersonDetection.objects.filter(detection_time__date=start_date).values('age').annotate(count=Count('age')).order_by('age')
    gender_data = PersonDetection.objects.filter(detection_time__date=start_date).values('gender').annotate(count=Count('gender')).order_by('gender')
    avg_time_spent = PersonDetection.objects.filter(detection_time__date=start_date).aggregate(avg_time_spent=Avg('time_spent'))['avg_time_spent'] or 0

    total_persons = PersonCount.objects.filter(date__date=start_date).aggregate(total=Sum('total_persons'))['total'] or 0 

    data = {
        'age_data': list(age_data),
        'gender_data': list(gender_data),
        'avg_time_spent': avg_time_spent,
        'total_persons': total_persons,
    }

    return JsonResponse(data)
