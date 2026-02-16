from django import forms
from django.contrib.auth.models import User
# from Tickets.models import Ticket, UserRole, TicketNote
from Tickets.models import Ticket, TicketNote
from django.core.exceptions import ValidationError
import re
from Tickets.services.permissions import get_assignees

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
                  # داینامیک کردن چکباکس
                  'attachments',
                  'send_notification', 'send_email', 'send_sms'
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
            # داینامیک کردن چکباکس
            'send_notification': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'send_email': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'send_sms': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

        labels = {
            'contact_name': 'Full Name',
            'contact_email': 'Email Address',
            'contact_phone': 'Phone Number',
            'max_replay_date': 'Maximum Reply Date',
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)


        for field in self.fields.values():
            field.required = False
            field.widget.attrs.update({
                    'class': 'form-control'
            })


        if self.request and self.request.user.is_authenticated:
            self.fields['users'].queryset = self.get_allowed_users()


        if self.instance and self.instance.pk:
                # اگر در حال ویرایش هستیم، کاربران assign شده فعلی را بگیر
            current_assignees = self.instance.assignments_tickets.values_list(
                'assignee_id', flat=True
            )
            self.fields['users'].initial = list(current_assignees)
        ticket = kwargs.get("instance")

        if ticket:
            self.fields['users'].initial = ticket.assignments_tickets.values_list(
                'assigned_ticket_id', flat=True
            )
        # if self.request and self.request.user.is_authenticated:
        #     allowed_users = get_assignees(self.request.user)
        #
        #     if isinstance(allowed_users, list):
        #         user_ids = [user.id if hasattr(user , 'id') else user for user in allowed_users]
        #         self.fields['users'].queryset = User.objects.filter(id__in=user_ids)
        #     else :
        #         self.fields['users'].queryset = allowed_users
        # else:
        #     self.fields['users'].querset = User.objects.none()

    # def get_allowed_users(self):
    #     """فقط کاربران پایین‌تر از سطح کاربر فعلی"""
    #     current_role = UserRole.objects.filter(user=self.request.user).first()
    #     if current_role:
    #         # کاربران با level بالاتر یا مساوی (عدد کمتر = سطح بالاتر)
    #         return User.objects.filter(
    #             user_roles__role__level__gte=current_role.role.level
    #         ).exclude(id=self.request.user.id).distinct()
    #     return User.objects.none()

    # def get_allowed_users(self):
    #     """فقط کاربران پایین‌تر از سطح کاربر فعلی"""
    #     from services.permissions import get_assignees
    #
    #     return get_assignees(self.request.user)

    def get_allowed_users(self):
        """فقط کاربران پایین‌تر از سطح کاربر فعلی"""
        return get_assignees(self.request.user)

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

class TicketNoteForm(forms.ModelForm):
    class Meta:
        model = TicketNote
        fields = ['content', 'is_private']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Write your note here...'
            }),
            'is_private': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        labels = {
            'content': 'Note text',
            'is_private': 'Private (staff only)'
        }


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # اطمینان از اینکه فیلدها required هستند
        self.fields['content'].required = True