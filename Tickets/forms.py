from django import forms
from django.contrib.auth.models import User
from Tickets.models import Ticket
from django.core.exceptions import ValidationError
import re

class MultiFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class TicketForm(forms.ModelForm):
    attachments = forms.FileField(
        widget=MultiFileInput(attrs={
            "multiple": True,
            "class":"form-control"
        }),
        required=False,
        help_text="You Can Upload Multiple files (PDF,Word,Images).")

    class Meta:
        model = Ticket
        fields = ['contact_name',
                  'contact_email',
                  'contact_phone',
                  'department',
                  'category',
                  'priority',
                  'subject',
                  'max_replay_date',
                  'tags',
                  'description',
                  'due_date',
                  ]
        exclude = ['created_by', 'closed_at', 'tracking_code', 'status']

        widgets = {
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Subject ...'}),
            'description': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Describe your Issue ...'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'tags': forms.SelectMultiple(attrs={'class': 'form-select'}),
            'max_replay_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'due_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'contact_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your full name'}),
            'contact_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'your@email.com'}),
            'contact_phone': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Your phone number', 'maxlength': '11',
                       'pattern': '[0-9]{10,11}', 'title': 'Please enter 10 or 11 digits'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
        }

        labels = {
            'contact_name': 'Full Name',
            'contact_email': 'Email Address',
            'contact_phone': 'Phone Number',
            'max_replay_date': 'Maximum Reply Date',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = False
            field.widget.attrs.update({
                'class': 'form-control'
            })

    # def clean_tags(self):
    #     tags = self.cleaned_data.get('tags')
    #     count = tags.count() if tags else 0
    #
    #     if count < 1:
    #         raise forms.ValidationError("Please enter at least one tag.")
    #     if count > 5:
    #         raise forms.ValidationError("Please enter at most 5 tags.")
    #
    #     return tags
    #
    # def clean_attachments(self):
    #     files = self.files.getlist('attachments')
    #     allowed_types =[
    #         'application/pdf',
    #         'application/msword',
    #         'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    #         'image/jpeg',
    #         'image/png',
    #     ]
    #     for f in files:
    #         if f.content_type not in allowed_types:
    #             raise forms.ValidationError(f"{f.name} has an unsupported file type.")
    #         if f.size > 5 * 1024 * 1024:
    #             raise forms.ValidationError(f"{f.name} exceeds 5 MB size limit.")
    #     return files