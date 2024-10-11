import cv2
import numpy as np
import time
from .models import PersonAgeGender, PersonDetection, PersonCount, ObjectDetection, ObjectRelatedPerson
import datetime

# Initialize global dictionary for tracking person positions and detection times
person_tracker = {}

def load_models():
    yolo_net = cv2.dnn.readNet('cafe_analysis_app/yolov3tiny/yolov3-tiny.cfg', 'cafe_analysis_app/yolov3tiny/yolov3-tiny.weights')
    classes = open("cafe_analysis_app/coco.names").read().strip().split("\n")

    age_net = cv2.dnn.readNetFromCaffe('cafe_analysis_app/caffe/deploy_age.prototxt', 'cafe_analysis_app/caffe/Age_net.caffemodel')
    gender_net = cv2.dnn.readNetFromCaffe('cafe_analysis_app/caffe/deploy_gender.prototxt', 'cafe_analysis_app/caffe/gender_net.caffemodel')

    return yolo_net, classes, age_net, gender_net

def yolo_object_detection(frame, net, classes, conf_threshold=0.25, nms_threshold=0.20):
    height, width = frame.shape[:2]
    blob = cv2.dnn.blobFromImage(frame, 1 / 255.0, (416, 416), swapRB=True, crop=False)
    net.setInput(blob)
    layer_names = net.getLayerNames()
    layer_outputs = net.forward([layer_names[i - 1] for i in net.getUnconnectedOutLayers()])

    boxes = []
    confidences = []
    class_ids = []

    for output in layer_outputs:
        for detection in output:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]

            if confidence > conf_threshold:
                box = detection[0:4] * np.array([width, height, width, height])
                (centerX, centerY, w, h) = box.astype("int")

                startX = int(centerX - (w / 2))
                startY = int(centerY - (h / 2))

                boxes.append([startX, startY, int(w), int(h)])
                confidences.append(float(confidence))
                class_ids.append(class_id)

    idxs = cv2.dnn.NMSBoxes(boxes, confidences, conf_threshold, nms_threshold)

    detections = []
    if len(idxs) > 0:
        for i in idxs.flatten():
            box = boxes[i]
            startX, startY, w, h = box
            class_id = class_ids[i]
            confidence = confidences[i]

            detections.append((class_id, confidence, startX, startY, w, h))

    return detections

def detect_age_gender(frame, person_blob, age_net, gender_net):
    GENDERS = ["Male", "Female"]
    AGE_BUCKETS = ["(0-2)", "(4-6)", "(8-12)", "(15-20)", "(25-32)", "(38-43)", "(48-53)", "(60-100)"]

    gender_net.setInput(person_blob)
    gender_preds = gender_net.forward()
    gender = GENDERS[gender_preds[0].argmax()]

    age_net.setInput(person_blob)
    age_preds = age_net.forward()
    age = AGE_BUCKETS[age_preds[0].argmax()]

    return gender, age

def track_dwell_time(centroid, frame, startX, startY, gender, age):
    current_time = time.time()
    today = datetime.date.today()  # Get today's date

    # Retrieve or create an entry for today
    person_count_obj, _ = PersonCount.objects.get_or_create(date=today)

    # Check if person exists in the tracker based on centroid movement
    for person_id, data in person_tracker.items():
        distance_moved = np.linalg.norm(np.array(centroid) - np.array(data['last_position']))

        if distance_moved < 100:
            # Update existing person info
            person_tracker[person_id]['last_position'] = centroid
            person_tracker[person_id]['positions'].append(centroid)  # Store the position for line drawing
            dwell_time = current_time - person_tracker[person_id]['initial_time']

            person = PersonDetection.objects.get(person_id=person_id)
            person.time_spent = dwell_time
            person.last_seen = datetime.datetime.now()
            person.save()

            # Annotate the frame with person data
            cv2.putText(frame, f"Dwell Time: {dwell_time:.1f}s", (startX, startY - 35), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            cv2.putText(frame, f"Person ID: {person_id}", (startX, startY - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            return  # Stop processing as we have updated an existing person

    # If it's a new person, generate a new person ID
    if PersonDetection.objects.exists():
        last_person = PersonDetection.objects.latest('person_id')
        new_person_id = last_person.person_id + 1
    else:
        new_person_id = 0

    # Track the new person
    person_tracker[new_person_id] = {
        'initial_time': current_time,
        'last_position': centroid,
        'positions': [centroid]  # Initialize positions for line drawing
    }

    # Save the new person in the database
    new_person = PersonDetection.objects.create(
        person_id=new_person_id,
        time_spent=0
    )

    # Save age and gender to PersonAgeGender model
    PersonAgeGender.objects.create(
        person_detection=new_person,
        age=age,
        gender=gender
    )

    # Update the person count for today
    person_count_obj.total_persons += 1
    person_count_obj.save()

    # Annotate the frame with new person data
    cv2.putText(frame, f"Person ID: {new_person_id}", (startX, startY - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

    # Return new person details for use in the alert
    return new_person_id, gender, age  # Return person ID, gender, and age

def add_object_detection(detections, classes):
    """
    Adds non-person objects detected to the ObjectDetection model.
    """
    for detection in detections:
        class_id, confidence, startX, startY, w, h = detection
        object_name = classes[class_id]

        if object_name != "person":  # Exclude persons
            # Check if the object already exists to avoid duplicates
            if not ObjectDetection.objects.filter(object_id=class_id).exists():
                ObjectDetection.objects.create(object_id=class_id, object_name=object_name)

# 
def process_detections(frame, detections, classes, age_net, gender_net):
    for detection in detections:
        class_id, confidence, startX, startY, w, h = detection
        centroid = (int(startX + w / 2), int(startY + h / 2))



        label=f"{classes[class_id]}:{confidence:.2f}"
        cv2.putText(frame,label,(startX,startY - 5),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

        if classes[class_id] == "person":
            person_blob = cv2.dnn.blobFromImage(frame, 1.0, (227, 227), (78.4263377603, 87.7689143744, 114.895847746))
            gender, age = detect_age_gender(frame, person_blob, age_net, gender_net)

            cv2.putText(frame, f"{gender}, {age}", (startX, startY - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

            track_dwell_time(centroid, frame, startX, startY, gender, age)

        # Process non-person objects and track their relations
        add_object_detection(detections, classes)
    
    return frame
