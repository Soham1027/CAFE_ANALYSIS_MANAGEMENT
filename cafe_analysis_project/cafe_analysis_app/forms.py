from django import forms
from .models import *

class Form(forms.ModelForm):
    
    class Meta:
        model = Person
        fields = "__all__"
       