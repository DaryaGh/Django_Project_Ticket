from django import forms
from Tickets.models import Ticket

class TicketForm(forms.ModelForm):

    class Meta:
        model = Ticket
        fields = ['contact_name',
            'contact_email',
            'contact_phone',
            'department',
            'category',
            'priority',
            'subject',
            'description',
            'tags',
            'max_replay_date',
            'due_date',
                  ]
        exclude = ['created_by', 'closed_at', 'tracking_code', 'status']

        widgets = {
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Subject ...'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Describe your Issue ...'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'tags': forms.SelectMultiple(attrs={'class': 'form-select'}),
            'max_replay_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'due_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'contact_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your full name'}),
            'contact_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'your@email.com'}),
            'contact_phone': forms.TextInput(attrs={'class': 'form-control','placeholder': 'Your phone number','maxlength': '11','pattern': '[0-9]{10,11}','title': 'Please enter 10 or 11 digits'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'contact_name': 'Full Name',
            'contact_email': 'Email Address',
            'contact_phone': 'Phone Number',
            'max_replay_date': 'Maximum Reply Date',
        }