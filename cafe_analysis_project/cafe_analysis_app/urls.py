# urls.py
from django.urls import path
from . import views
from .process_video import start_video_processing,stop_video_processing,video_feed

urlpatterns = [
    path('start-video/', start_video_processing, name='start_video'),
    path('video_feed/', video_feed, name='video_feed'),

    path('stop-video/', stop_video_processing, name='stop_video'),

    path('dashboard/',views.dashboard_view, name='dashboard'),

   
]
