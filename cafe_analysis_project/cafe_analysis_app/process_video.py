import cv2
import logging
from .detection_utils import load_models, yolo_object_detection, process_detections

logger = logging.getLogger(__name__)

from django.http import HttpResponse, StreamingHttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import threading

class VideoProcessor:
    def __init__(self, stream_url):
        self.stream_url = stream_url
        self.stop_event = threading.Event()
        self.video_thread = None
        self.cap = None

    def start(self):
        if self.video_thread and self.video_thread.is_alive():
            return False  # Already running
        self.stop_event.clear()
        self.cap = cv2.VideoCapture(self.stream_url)  # Initialize capture object here
        self.video_thread = threading.Thread(target=self.process_video)
        self.video_thread.start()
        return True

    def stop(self):
        if self.video_thread and self.video_thread.is_alive():
            self.stop_event.set()
            self.video_thread.join()  # Wait for the thread to finish
            self.cleanup()
            self.reset()  # Reset the video processor

    def reset(self):
        self.cap = None  

    def process_video(self):
        logger.info(f"Starting live video processing from {self.stream_url}")

        # Load models once for efficiency
        yolo_net, classes, age_net, gender_net = load_models()

        self.cap = cv2.VideoCapture(self.stream_url)
        if not self.cap.isOpened():
            logger.error(f"Failed to open video stream {self.stream_url}")
            return

        while self.cap.isOpened():
            if self.stop_event.is_set():
                logger.info("Stop event received, stopping video processing.")
                break

            ret, frame = self.cap.read()
            if not ret:
                logger.error("Failed to read frame from stream")
                break

            # Perform YOLO object detection
            detections = yolo_object_detection(frame, yolo_net, classes, target_class_ids=[0])

            # Process detections (e.g., annotate frame with age and gender)
            frame = process_detections(frame, detections, classes, age_net, gender_net)

        self.cleanup()

    def cleanup(self):
        if self.cap:
            self.cap.release()  # Release the video capture object
            self.cap = None
        cv2.destroyAllWindows()
        logger.info("Live video processing finished and resources cleaned up")

# Initialize global video processor for the stream
video_processor = VideoProcessor('cafe_analysis_app/2.mp4')

@csrf_exempt
def start_video_processing(request):
    if not video_processor.start():
        return HttpResponse("Video is already running")
    return HttpResponse("Live video processing started")

@csrf_exempt
def stop_video_processing(request):
    video_processor.stop()
    return HttpResponse("Live video processing stopped")

# Stream frames for video feed
import cv2
import numpy as np
import logging

# Set up logger
logger = logging.getLogger(__name__)

def generate_frames(stream_url):
    logger.info(f"Opening video stream {stream_url}")

    # Load models (ensure the models are quantized if possible)
    yolo_net, classes, age_net, gender_net = load_models()

    cap = cv2.VideoCapture(stream_url)
    if not cap.isOpened():
        logger.error(f"Failed to open video stream {stream_url}")
        return

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            logger.error("No frame to read")
            break

        # Ensure the frame is in the right format
        if frame.dtype != np.uint8:
            # Convert to 8-bit precision if necessary
            frame = cv2.convertScaleAbs(frame)
        
        # Check for correct range
        frame = np.clip(frame, 0, 255)

        # Perform object detection and other processing on the quantized frame
        detections = yolo_object_detection(frame, yolo_net, classes, target_class_ids=[0])
        frame = process_detections(frame, detections, classes, age_net, gender_net)

        # Encode the frame to JPEG
        ret, jpeg = cv2.imencode('.jpg', frame)
        if not ret:
            logger.error("Failed to encode frame")
            continue

        # Prepare the frame for streaming
        frame = jpeg.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

    cap.release()


def video_feed(request):
    stream_url = 'cafe_analysis_app/2.mp4'
    return StreamingHttpResponse(generate_frames(stream_url), content_type='multipart/x-mixed-replace; boundary=frame')