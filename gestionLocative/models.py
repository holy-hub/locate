from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Propriete(models.Model):
    nb_etage = models.CharField(max_length=20)
    adresse = models.CharField(max_length=50)
    designation = models.CharField(max_length=50)
    ville = models.CharField(max_length=20, blank=True)
    code_postal = models.CharField(max_length=20, blank=True)
    description = models.TextField(blank=True)
    nb_chambre = models.PositiveSmallIntegerField()
    surface = models.DecimalField(max_digits=6, decimal_places=2)
    montant = models.DecimalField(max_digits=15, decimal_places=2)
    proprietaire = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='proprietaire')
    locataire = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='locataire')
    demande_allocation = models.BooleanField(default=False)
    n = models.IntegerField(default=0)
    est_loue = models.BooleanField(default=False)
    def __str__(self): return self.proprietaire.username + " ( "+self.ville+" )"

class Facture(models.Model):
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE)
    propriete = models.ForeignKey(Propriete, on_delete=models.CASCADE)
    montantFacture = models.DecimalField(max_digits=8, decimal_places=2)
    date_facturation = models.DateField(auto_now_add=True)
    est_paye = models.BooleanField(default=False)
    def __str__(self): return f"Facture #{self.utilisateur.username}"

class Location(models.Model):
    utilisateur = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='propriete_loc')
    propriete = models.ForeignKey(Propriete, on_delete=models.SET_NULL, null=True, related_name='propriete_loc')
    montantLocation = models.PositiveIntegerField(default=0)
    date_debut = models.DateField(auto_now_add=True)
    date_fin = models.DateField()
    est_autorisee = models.BooleanField(default=False)
    def __str__(self):
        return f"Location #{self.utilisateur.username}"

class Document(models.Model):
    utilisateur = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='utilisateur_doc')
    propriete = models.ForeignKey(Propriete, on_delete=models.SET_NULL, null=True, related_name='propriete_doc')
    titre = models.CharField(max_length=100)
    fichier = models.FileField(upload_to='documents/')
    def __str__(self): return self.titre
    
