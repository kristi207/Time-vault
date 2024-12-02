from django import forms
from .models import Letter
from django.utils import timezone

class LetterForm(forms.ModelForm):
    class Meta:
        model = Letter
        fields = ['recipient_email', 'content', 'send_date', 'title', 'is_public']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set the default send_date to today's date and time
        self.fields['send_date'].initial = timezone.now()
        
        # Set widget for send_date as a datetime-local input
        self.fields['send_date'].widget = forms.DateTimeInput(attrs={
            'type': 'datetime-local',
            'min': timezone.now().strftime('%Y-%m-%dT%H:%M'),  # Set the minimum date/time as the current time
        })
        
        # Make title optional and hide it initially
        self.fields['title'].required = False
