from django.db import models

class PersonDetection(models.Model):
    person_id = models.IntegerField(unique=True)  # Unique ID for each person detected
    time_spent = models.FloatField()  # Time spent in seconds
    detection_time = models.DateTimeField(auto_now_add=True)  # When the detection occurred
    last_seen = models.DateTimeField(auto_now=True)  # Last time the person was detected

    def __str__(self):
        return f'Person {self.person_id}'


class PersonCount(models.Model):
    data_id = models.AutoField(primary_key=True)  # Auto-incremented unique ID
    total_persons = models.IntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)
    date = models.DateTimeField(auto_now_add=True, unique=True)  # When the detection occurred

    def __str__(self):
        return f'Data {self.data_id} - {self.date}'


class PersonAgeGender(models.Model):
    person_detection = models.ForeignKey(PersonDetection, on_delete=models.CASCADE, related_name='age_gender_info')
    age = models.CharField(max_length=50)
    gender = models.CharField(max_length=10)

    def __str__(self):
        return f'Person {self.person_detection.person_id} - Age: {self.age}, Gender: {self.gender}'
