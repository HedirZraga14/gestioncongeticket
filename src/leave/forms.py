from django import forms
from .models import Leave
import datetime

class LeaveCreationForm(forms.ModelForm):
	
	class Meta:
		model = Leave
		exclude = ['user','defaultdays','hrcomments','status','is_approved','updated','created']

	def clean_enddate(self):
		enddate = self.cleaned_data['enddate']
		startdate = self.cleaned_data['startdate']
		today_date = datetime.date.today()

		if (startdate or enddate) < today_date:# both dates must not be in the past
			raise forms.ValidationError("Selected dates are incorrect,please select again")

		elif startdate >= enddate:# TRUE -> FUTURE DATE > PAST DATE,FALSE other wise
			raise forms.ValidationError("Selected dates are wrong")

		return enddate

class SimplifiedLeaveForm(forms.ModelForm):
    """
    Formulaire simplifié pour la demande de congés
    Contient seulement : date début, date fin, type congé, facteurs d'approbation IA
    """
    
    # Facteurs d'approbation IA avec checkboxes
    FACTEURS_APPROBATION = [
        ('urgent', 'Demande urgente'),
        ('sante', 'Problème de santé'),
        ('familial', 'Raison familiale'),
        ('formation', 'Formation professionnelle'),
        ('personnel', 'Raison personnelle'),
        ('vacances', 'Vacances annuelles'),
        ('evenement', 'Événement spécial'),
        ('autre', 'Autre raison'),
    ]
    
    ai_approval_factors = forms.MultipleChoiceField(
        choices=FACTEURS_APPROBATION,
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-check-input',
        }),
        label='Facteurs d\'approbation IA',
        required=True,
        help_text='Sélectionnez tous les facteurs qui s\'appliquent à votre demande'
    )
    
    class Meta:
        model = Leave
        fields = ['startdate', 'enddate', 'leavetype']
        labels = {
            'startdate': 'Date de début',
            'enddate': 'Date de fin', 
            'leavetype': 'Type de congé',
        }
        widgets = {
            'startdate': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'required': True
            }),
            'enddate': forms.DateInput(attrs={
                'class': 'form-control', 
                'type': 'date',
                'required': True
            }),
            'leavetype': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
        }

    def clean_enddate(self):
        enddate = self.cleaned_data['enddate']
        startdate = self.cleaned_data['startdate']
        today_date = datetime.date.today()

        if (startdate or enddate) < today_date:
            raise forms.ValidationError("Les dates sélectionnées sont incorrectes, veuillez sélectionner des dates futures")

        elif startdate >= enddate:
            raise forms.ValidationError("La date de fin doit être postérieure à la date de début")

        return enddate

    def clean_ai_approval_factors(self):
        facteurs = self.cleaned_data.get('ai_approval_factors', [])
        if not facteurs:
            raise forms.ValidationError("Veuillez sélectionner au moins un facteur d'approbation")
        return ', '.join(facteurs)  # Convertir la liste en chaîne pour la base de données

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ajouter des messages d'aide
        self.fields['ai_approval_factors'].help_text = 'Ces facteurs seront analysés par l\'IA pour évaluer votre demande'





