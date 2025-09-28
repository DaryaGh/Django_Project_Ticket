from django import forms
from Tickets.models import Ticket

class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['category','priority','subject','description','tags','max_replay_date']
        # fields = '__all__'
        widgets = {
            'subject': forms.TextInput(attrs={'class':'form-control','placeholder':'Enter Subject ...'}),
            'description': forms.Textarea(attrs={'class':'form-control', 'rows':5 ,'placeholder':'Describe your Issue ...'}),
            'priority': forms.Select(attrs={'class':'form-select'}),
            'category': forms.Select(attrs={'class':'form-select'}),
            'tags': forms.SelectMultiple(attrs={'class':'form-select'}),
            'max_replay_date': forms.DateTimeInput(attrs={'class':'form-control','type':'datetime-local'}),
        }