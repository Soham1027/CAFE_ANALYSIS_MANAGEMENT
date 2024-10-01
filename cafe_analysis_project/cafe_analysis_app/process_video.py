import cv2
import logging
from .detection_utils import load_models, yolo_object_detection, process_detections

logger = logging.getLogger(__name__)

from django.http import HttpResponse, StreamingHttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import threading


video_thread = None
video_stop = threading.Event()

import threading
import cv2
from django.http import StreamingHttpResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import logging

logger = logging.getLogger(__name__)

# Assuming the existence of these helper functions:
# - load_models: Load YOLO, age, and gender detection models
# - yolo_object_detection: Perform object detection using YOLO
# - process_detections: Process detections (age/gender) and annotate the frame

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
        self.video_thread = threading.Thread(target=self.process_video)
        self.video_thread.start()
        return True

    def stop(self):
        if self.video_thread and self.video_thread.is_alive():
            self.stop_event.set()
            self.video_thread.join()

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

            # Optional: Display frame (commented for optimization)
            # cv2.imshow('Live Feed', frame)

        self.cleanup()

    def cleanup(self):
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
        logger.info("Live video processing finished")

# Initialize global video processor for the stream
video_processor = VideoProcessor('cafe_analysis_app/1.mp4')

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
def generate_frames(stream_url):
    logger.info(f"Opening video stream {stream_url}")
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

        # Perform object detection and process frame
        detections = yolo_object_detection(frame, yolo_net, classes, target_class_ids=[0])
        frame = process_detections(frame, detections, classes, age_net, gender_net)

        ret, jpeg = cv2.imencode('.jpg', frame)
        if not ret:
            logger.error("Failed to encode frame")
            continue

        frame = jpeg.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

    cap.release()


def video_feed(request):
    # stream_url = 'http://192.168.29.113:4747/video'
    stream_url = 'cafe_analysis_app/1.mp4'

    return StreamingHttpResponse(generate_frames(stream_url), content_type='multipart/x-mixed-replace; boundary=frame')


# @csrf_exempt
# def start_video_processing(request):
#     global video_thread, video_stop
#     if video_thread and video_thread.is_alive():
#         return HttpResponse("Video is already running")
    
#     # Reset the stop event
#     video_stop.clear()

#     stream_url = 'http://192.168.29.113:4747/video'
    
#     # Start processing video in a separate thread
#     video_thread = threading.Thread(target=process_live_video_with_stop, args=(stream_url, video_stop))
#     video_thread.start()

#     return HttpResponse("Live video processing started")

# @csrf_exempt
# def stop_video_processing(request):
#     global video_thread, video_stop
#     if video_thread and video_thread.is_alive():
#         # Set stop flag to stop the thread
#         video_stop.set()

#         # Wait for thread to finish
#         video_thread.join()

#     return HttpResponse("Live video processing stopped")

# # Modified version of process_live_video to check for stop event
# def process_live_video_with_stop(stream_url, stop_event):
#     logger.info(f"Starting live video processing from {stream_url}")

#     # Load models
#     yolo_net, classes, age_net, gender_net = load_models()

#     # Open video stream
#     cap = cv2.VideoCapture(stream_url)

#     if not cap.isOpened():
#         logger.error(f"Failed to open video stream {stream_url}")
#         return

#     while cap.isOpened():
#         if stop_event.is_set():
#             logger.info("Stop event received, stopping video processing.")
#             break

#         ret, frame = cap.read()
#         if not ret:
#             break

#         # Perform YOLO object detection
#         detections = yolo_object_detection(frame, yolo_net, classes, target_class_ids=[0])

#         # Process detections
#         frame = process_detections(frame, detections, classes, age_net, gender_net)

#         # Display the resulting frame
#         # cv2.imshow('Live Feed', frame)

#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             break

#     cap.release()
#     cv2.destroyAllWindows()
#     logger.info("Live video processing finished")



# def generate_frames(stream_url):
#     # Load models
#     yolo_net, classes, age_net, gender_net = load_models()

#     # Open video stream
#     cap = cv2.VideoCapture(stream_url)

#     if not cap.isOpened():
#         logger.error(f"Failed to open video stream {stream_url}")
#         return

#     while cap.isOpened():
#         ret, frame = cap.read()
#         if not ret:
#             break

#         # Perform YOLO object detection
#         detections = yolo_object_detection(frame, yolo_net, classes, target_class_ids=[0])

#         # Process detections
#         frame = process_detections(frame, detections, classes, age_net, gender_net)

#         # Encode the frame as JPEG
#         ret, jpeg = cv2.imencode('.jpg', frame)
#         frame = jpeg.tobytes()

#         # Yield the frame as part of the stream
#         yield (b'--frame\r\n'
#                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

#     cap.release()

# def video_feed(request):
#     stream_url = 'http://192.168.29.113:4747/video'
#     return StreamingHttpResponse(generate_frames(stream_url), content_type='multipart/x-mixed-replace; boundary=frame')
# def process_live_video(stream_url):
#     logger.info(f"Starting live video processing from {stream_url}")

#     # Load models
#     yolo_net, classes, age_net, gender_net = load_models()

#     # Open video stream
#     cap = cv2.VideoCapture(stream_url)

#     if not cap.isOpened():
#         logger.error(f"Failed to open video stream {stream_url}")
#         return

#     while cap.isOpened():
#         ret, frame = cap.read()
#         if not ret:
#             break

#         # Perform YOLO object detection
#         detections = yolo_object_detection(frame, yolo_net, classes, target_class_ids=[0])  # Assuming '0' is the class ID for 'person'

#         # Process detections
#         frame = process_detections(frame, detections, classes, age_net, gender_net)

#         # Display the resulting frame
#         cv2.imshow('Live Feed', frame)

#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             break

#     cap.release()
#     cv2.destroyAllWindows()
#     logger.info("Live video processing finished")
