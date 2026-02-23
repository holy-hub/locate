from django import forms
from .models import (
    Propriete, Location, Facture, Document, Intervention,
    TypePropriete, TypeDocument,
)


class ProprieteForm(forms.ModelForm):
    """Formulaire création/édition propriété (propriétaire défini dans la vue)."""
    class Meta:
        model = Propriete
        fields = [
            'type_propriete', 'designation', 'description',
            'adresse', 'complement_adresse', 'code_postal', 'ville',
            'nb_etage', 'nb_chambre', 'surface', 'montant',
            'charges_comprises', 'montant_charges', 'garantie',
            'photo',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'type_propriete': forms.Select(choices=TypePropriete.choices),
        }


class PayerFactureForm(forms.Form):
    montant = forms.DecimalField(min_value=0, decimal_places=2)


class DemanderLocationForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = ['date_fin', 'message_demande']
        widgets = {
            'date_fin': forms.DateInput(attrs={'type': 'date'}),
            'message_demande': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Message optionnel au propriétaire'}),
        }


class TelechargerDocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['type_document', 'titre', 'fichier']
        widgets = {
            'type_document': forms.Select(choices=TypeDocument.choices),
        }


class InterventionForm(forms.ModelForm):
    class Meta:
        model = Intervention
        fields = ['titre', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }
