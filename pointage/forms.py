from django import forms
from django.contrib.admin.widgets import AdminSplitDateTime
SALLE_CHOICES = [
    ('A', 'Atelier'),
    ('B', "Bureau d'étude"),
    ('D', 'Découpe laser')
]
class ChooseRoom(forms.Form):
    salle = forms.ChoiceField(choices=SALLE_CHOICES, required=True)

class ReserveForm(forms.Form):
    entree = forms.DateTimeField(input_formats=['%d/%m/%Y %H:%M'], widget=forms.TextInput(attrs={'class': 'form-control '}))
    sortie = forms.DateTimeField(input_formats=['%d/%m/%Y %H:%M'],
                                 widget=forms.TextInput(attrs={'class': 'form-control '}))
    salle = forms.ChoiceField(choices=SALLE_CHOICES, required=True)

class SignIn(forms.Form):
    pseudo = forms.CharField(max_length=30, required=True,
                                     widget=forms.TextInput(attrs={'class': 'form-control'}))
    passw = forms.CharField(max_length=30,label="Mot de passe", required=True, widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    fields = ('Pseudo', 'Mot de passe')

class Add(forms.Form):
    nom = forms.CharField(max_length=30, required=True,
                                     widget=forms.TextInput(attrs={'class': 'form-control '}))

    prenom = forms.CharField(max_length=30, required=True,
                             widget=forms.TextInput(attrs={'class': 'form-control'}))

    asso = forms.CharField(max_length=30, required=True,
                             widget=forms.TextInput(attrs={'class': 'form-control'}))

    fields = ('nom','prenom','asso')

class ChangePasswordForm(forms.Form):
    passw = forms.CharField(max_length=30, label="Mot de passe", required=True,
                            widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    passw2 = forms.CharField(max_length=30, label="Répetez", required=True,
                            widget=forms.PasswordInput(attrs={'class': 'form-control'}))

