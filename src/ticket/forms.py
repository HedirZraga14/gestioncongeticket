from django import forms
from .models import Ticket
from .models import Beneficiaire
from django.contrib.auth.models import User
import datetime

class ticketForm(forms.ModelForm):
    retraité = forms.BooleanField(required=False, widget=forms.CheckboxInput)
    beneficiaires = forms.ModelMultipleChoiceField(queryset=Beneficiaire.objects.all(), required=False, widget=forms.CheckboxSelectMultiple)

    class Meta:
        model = Ticket
        fields = [ 'destination', 'compagnie','retraité', 'vous','beneficiaires','created_at']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'vous': forms.RadioSelect(choices=[(True, 'Oui'), (False, 'Non')])
        }
        # exclude 'created_at' field as it is non-editable
        exclude = ['created_at']

class BeneficiaireCreateForm(forms.ModelForm):
    user = forms.ModelChoiceField(queryset=User.objects.all())
    date_naissance = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = Beneficiaire
        fields = ('user', 'nom_et_prenom', 'date_naissance')

