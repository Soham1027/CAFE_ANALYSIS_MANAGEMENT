from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import threading
from .process_video import process_live_video

@csrf_exempt
def start_video_processing(request):
    # Replace with the actual IP address and port of your DroidCam server
    stream_url = 'http://192.168.29.113:4747/video'
    
    # Start processing video in a separate thread
    video_thread = threading.Thread(target=process_live_video, args=(stream_url,))
    video_thread.start()
    return HttpResponse("Live video processing started")
