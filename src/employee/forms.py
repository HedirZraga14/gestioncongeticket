from django import forms
from employee.models import Employee
from django.contrib.auth.models import User

class EmployeeCreateForm(forms.ModelForm):
    employeeid = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'entrer votre matricule'}))
    image = forms.ImageField(required=False,widget=forms.FileInput(attrs={'onchange':'previewImage(this);'}))
    employeetype = forms.ChoiceField(choices=[('sol', 'Personnel au sol'), ('technique', 'Personnel navigant technique'), ('commercial', 'Personnel navigant commercial')])

       
    class Meta:
        model = Employee
        exclude = ['is_blocked','is_deleted','created','updated']
        widgets = {
            'bio':forms.Textarea(attrs={'cols':5,'rows':5})
        }