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
            "class": "form-control"
        }),
        required=False,
        help_text="You Can Upload Multiple files (PDF,Word,Images).")

    users = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        # widget=forms.SelectMultiple(attrs={'class': 'form-select'}),
        label="Select Users",
        help_text="Choose Multiple Users ...",
        required=True,
    )

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
                  'users',
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
            # 'users': forms.ModelMultipleChoiceField(attrs={'class': 'form-select'}),
            'users': forms.SelectMultiple(attrs={'class': 'form-select'}),
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

        ticket = kwargs.get("instance")
        # if ticket:
        #     self.fields['users'].initial = ticket.assignments.values_list(
        #         'assigned_id', flat=True
        #     )
        if ticket:
            self.fields['users'].initial = ticket.assignments_tickets.values_list(
                'assigned_ticket_id', flat=True  # یا 'assignee_id' بسته به نام فیلد
            )

    # def clean_users(self):
    #     users = self.cleaned_data.get('users')
    #     count = users.count() if users else 0
    #
    #     if count < 1:
    #         raise forms.ValidationError('Please select at least one user')
    #     return users

class RegisterForm(forms.ModelForm):
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter Password'}),
    )
    password2 = forms.CharField(
        label="Password Confirmation",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password'}),
    )

    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Username'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter Email'}),
        }
        labels = {
            'username': 'Username',
            'email': 'Email Address',
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if len(username) < 4:
            raise ValidationError('Username must be at least 4 characters long')
        if User.objects.filter(username=username).exists():
            raise ValidationError('Username already exists')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')

        # if len(email) == 0 :
        #     raise ValidationError('Email Address is required')

        if not email or len(email.strip()) == 0:
            raise ValidationError('Email Address is required')

        if User.objects.filter(email=email).exists():
            raise ValidationError('Email already exists')
        return email

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise ValidationError('Passwords must match')

        if password1 and len(password1) < 8:
            raise ValidationError('Password must be at least 8 characters long')

        if password1 and not re.search(r'\d', password1):
            raise ValidationError('Password must contain at least 1 digit')

        if password1 and not re.search(r'[A-Z]', password1):
            raise ValidationError('Password must contain at least one uppercase letter')

        if password1 and not re.search(r'[a-z]', password1):
            raise ValidationError('Password must contain at least one lowercase letter')

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user