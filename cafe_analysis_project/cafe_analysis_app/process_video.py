import cv2
import logging
from .detection_utils import load_models, yolo_object_detection, process_detections

logger = logging.getLogger(__name__)

def process_live_video(stream_url):
    logger.info(f"Starting live video processing from {stream_url}")

    # Load models
    yolo_net, classes, age_net, gender_net = load_models()

    # Open video stream
    cap = cv2.VideoCapture(stream_url)

    if not cap.isOpened():
        logger.error(f"Failed to open video stream {stream_url}")
        return

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Perform YOLO object detection
        detections = yolo_object_detection(frame, yolo_net, classes, target_class_ids=[0])  # Assuming '0' is the class ID for 'person'

        # Process detections
        frame = process_detections(frame, detections, classes, age_net, gender_net)

        # Display the resulting frame
        cv2.imshow('Live Feed', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    logger.info("Live video processing finished")
