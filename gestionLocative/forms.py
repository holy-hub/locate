from django import forms
from .models import *

class PayerFactureForm(forms.Form):
    montant = forms.DecimalField()
    # Autres champs requis pour le traitement du paiement

class DemanderLocationForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = ['date_fin']
        widgets = {
            'date_fin': forms.DateInput(attrs={'class': 'datepicker'}),
        }

class AutoriserLocationForm(forms.Form):
    motif = forms.CharField(max_length=200)

class CreerDocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ["fichier"]

class TelechargerDocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['titre', 'fichier']
 
class ProprieteForm(forms.ModelForm):
    class Meta:
        model = Propriete
        fields = ["nb_etage", "adresse", "ville", "code_postal", "description", "nb_chambre", "surface", "proprietaire",]
