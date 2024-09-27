# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('start-video/', views.start_video_processing, name='start_video'),
]
