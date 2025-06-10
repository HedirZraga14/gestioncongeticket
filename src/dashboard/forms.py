from django import forms
from employee.models import Employee

class SuperuserProfileForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['firstname', 'lastname', 'birthday', 'department', 'image', 'employeetype', 'is_blocked', 'is_deleted']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add custom classes and placeholders
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'form-control',
                'placeholder': field.label
            })
            
        # Add custom labels
        self.fields['image'].label = 'Photo de profil'
        self.fields['employeetype'].label = 'Type d'employé'
        self.fields['is_blocked'].label = 'Compte bloqué'
        self.fields['is_deleted'].label = 'Compte supprimé'
        
        # Add help text
        self.fields['birthday'].help_text = 'Format: JJ/MM/AAAA'
        self.fields['image'].help_text = 'Taille maximale: 5MB'
        
        # Make fields optional
        self.fields['image'].required = False
        self.fields['birthday'].required = False
