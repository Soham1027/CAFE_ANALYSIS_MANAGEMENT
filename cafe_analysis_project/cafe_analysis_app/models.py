# surveillance/models.py

from django.db import models
from django.utils import timezone

# Model to store detected person details
class Person(models.Model):
    person_id = models.AutoField(primary_key=True)
    gender = models.CharField(max_length=10, null=True, blank=True)
    age_range = models.CharField(max_length=15, null=True, blank=True)
    first_detected = models.DateTimeField(default=timezone.now)
    last_seen = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Person {self.person_id} - Gender: {self.gender}, Age: {self.age_range}"


# Model to store dwell time for each detected person
class DwellTime(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    total_dwell_time = models.FloatField(default=0.0)  # Store dwell time in seconds

    def __str__(self):
        return f"Dwell Time for Person {self.person.person_id}: {self.total_dwell_time:.2f} seconds"


# Model to store object details (optional)
class Object(models.Model):
    object_id = models.AutoField(primary_key=True)
    object_type = models.CharField(max_length=50)  # e.g., "person", "chair", "pet", etc.
    confidence = models.FloatField()
    first_detected = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Object {self.object_id} - Type: {self.object_type}, Confidence: {self.confidence:.2f}"
