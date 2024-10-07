# urls.py
from django.urls import path
from . import views
from .process_video import start_video_processing,stop_video_processing,video_feed

urlpatterns = [
    path('start-video/', start_video_processing, name='start_video'),
    path('video_feed/', video_feed, name='video_feed'),

    path('stop-video/', stop_video_processing, name='stop_video'),

    path('dashboard/',views.dashboard_view, name='dashboard'),
    path('get-dashboard-data/', views.get_dashboard_data, name='get_dashboard_data'),
   
    path('get-person-info/', views.get_person_info, name='get_person_info'), 
]
