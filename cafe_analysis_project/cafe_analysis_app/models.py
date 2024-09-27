# models.py
from django.db import models

class PersonDetection(models.Model):
    person_id = models.IntegerField()  # Unique ID for each person detected
    age = models.CharField(max_length=50)
    gender = models.CharField(max_length=10)
    time_spent = models.FloatField()  # Time spent in seconds
    detection_time = models.DateTimeField(auto_now_add=True)  # When the detection occurred
    last_seen = models.DateTimeField(auto_now=True)  # Last time the person was detected

class PersonCount(models.Model):
    total_persons = models.IntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)
