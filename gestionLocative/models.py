from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser

# --- Rôle utilisateur (profil) ---
class User(AbstractBaseUser):
    ROLE_PROPRIO = 'PROPRIO'
    ROLE_LOCA = 'LOCA'
    ROLE_CHOICES = [
        (ROLE_PROPRIO, 'Propriétaire'),
        (ROLE_LOCA, 'Locataire'),]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_LOCA)

    def __str__(self):
        return f'{self.username} — {self.get_role_display()}'

# --- Choix énumérés pour cohérence ---
class TypePropriete(models.TextChoices):
    APPARTEMENT = 'APP', 'Appartement'
    MAISON = 'MAI', 'Maison'
    STUDIO = 'STU', 'Studio'
    LOCAL_COMMERCIAL = 'LOC', 'Local commercial'
    AUTRE = 'AUT', 'Autre'

class StatutPropriete(models.TextChoices):
    DISPONIBLE = 'DIS', 'Disponible'
    LOUE = 'LOU', 'Loué'
    EN_MAINTENANCE = 'MAI', 'En maintenance'
    RESERVE = 'RES', 'Réservé'

class StatutLocation(models.TextChoices):
    EN_ATTENTE = 'ATT', 'En attente'
    ACCEPTEE = 'ACC', 'Acceptée'
    REFUSEE = 'REF', 'Refusée'
    TERMINEE = 'TER', 'Terminée'

class TypeFacture(models.TextChoices):
    LOYER = 'LOY', 'Loyer'
    CHARGES = 'CHA', 'Charges'
    REGULARISATION = 'REG', 'Régularisation'
    AUTRE = 'AUT', 'Autre'

class TypeDocument(models.TextChoices):
    CONTRAT = 'CON', 'Contrat de location'
    IDENTITE = 'IDE', 'Pièce d\'identité'
    JUSTIFICATIF = 'JUS', 'Justificatif de domicile'
    AUTRE = 'AUT', 'Autre'

class StatutIntervention(models.TextChoices):
    OUVERTE = 'OUV', 'Ouverte'
    EN_COURS = 'COU', 'En cours'
    CLOTUREE = 'CLO', 'Clôturée'

# --- Modèles ---

class Propriete(models.Model):
    """Bien immobilier à louer."""
    type_propriete = models.CharField(max_length=3, choices=TypePropriete.choices, default=TypePropriete.APPARTEMENT)
    designation = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    adresse = models.CharField(max_length=200)
    complement_adresse = models.CharField(max_length=100, blank=True)
    code_postal = models.CharField(max_length=20, blank=True)
    ville = models.CharField(max_length=80)
    nb_etage = models.CharField(max_length=20, blank=True, help_text="Étage ou nombre d'étages")
    nb_chambre = models.PositiveSmallIntegerField(default=1)
    surface = models.DecimalField(max_digits=8, decimal_places=2, help_text="Surface en m²")
    montant = models.DecimalField(max_digits=12, decimal_places=2, help_text="Loyer mensuel")
    charges_comprises = models.BooleanField(default=False, help_text="Charges incluses dans le loyer")
    montant_charges = models.DecimalField(
        max_digits=8, decimal_places=2, default=0, blank=True,
        help_text="Montant des charges si non comprises")
    garantie = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, blank=True,
        help_text="Dépôt de garantie")
    statut = models.CharField(
        max_length=3, choices=StatutPropriete.choices, default=StatutPropriete.DISPONIBLE)
    photo = models.ImageField(upload_to='proprietes/', blank=True, null=True)

    proprietaire = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name='proprietes_owned')
    locataire = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='proprietes_louees')
    demande_allocation = models.BooleanField(default=False)
    n = models.PositiveIntegerField(default=0, help_text="Nombre de demandes refusées (nb_refus)")
    est_loue = models.BooleanField(default=False)

    date_creation = models.DateTimeField(default=timezone.now)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Propriété"
        verbose_name_plural = "Propriétés"
        ordering = ['-date_creation']

    def __str__(self):
        if self.proprietaire:
            return f"{self.designation} ({self.ville}) — {self.proprietaire.username}"
        return f"{self.designation} ({self.ville})"

    def loyer_total(self):
        """Loyer + charges si non comprises."""
        if self.charges_comprises:
            return self.montant
        return self.montant + self.montant_charges


class Location(models.Model):
    """Demande ou contrat de location."""
    utilisateur = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name='locations')
    propriete = models.ForeignKey(
        Propriete, on_delete=models.SET_NULL, null=True, related_name='locations')
    montantLocation = models.DecimalField(
        max_digits=12, decimal_places=2, default=0,
        help_text="Montant total de la location (calculé à l'acceptation)")
    date_debut = models.DateField(auto_now_add=True)
    date_fin = models.DateField()
    est_autorisee = models.BooleanField(default=False)

    statut = models.CharField(
        max_length=3, choices=StatutLocation.choices, default=StatutLocation.EN_ATTENTE)
    motif_refus = models.CharField(max_length=255, blank=True)
    date_reponse = models.DateTimeField(null=True, blank=True)
    message_demande = models.TextField(blank=True, help_text="Message du demandeur")

    date_creation = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = "Location"
        verbose_name_plural = "Locations"
        ordering = ['-date_creation']

    def __str__(self):
        user = self.utilisateur.username if self.utilisateur else "?"
        return f"Location #{self.id} — {user} — {self.propriete.designation if self.propriete else '?'}"

    @property
    def duree_mois(self):
        if not self.date_debut or not self.date_fin:
            return 0
        months = (self.date_fin.year - self.date_debut.year) * 12
        months += self.date_fin.month - self.date_debut.month
        return max(1, months)


class Facture(models.Model):
    """Facture (loyer, charges, etc.)."""
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE, related_name='factures')
    propriete = models.ForeignKey(Propriete, on_delete=models.CASCADE, related_name='factures')
    location = models.ForeignKey(
        Location, on_delete=models.SET_NULL, null=True, blank=True, related_name='factures')
    type_facture = models.CharField(
        max_length=3, choices=TypeFacture.choices, default=TypeFacture.LOYER)
    montantFacture = models.DecimalField(max_digits=10, decimal_places=2)
    date_facturation = models.DateField(auto_now_add=True)
    date_echeance = models.DateField(null=True, blank=True)
    date_paiement = models.DateField(null=True, blank=True)
    periode = models.CharField(
        max_length=7, blank=True,
        help_text="Période concernée (format AAAA-MM)")
    est_paye = models.BooleanField(default=False)
    reference = models.CharField(max_length=50, blank=True)

    date_creation = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = "Facture"
        verbose_name_plural = "Factures"
        ordering = ['-date_facturation']

    def __str__(self):
        return f"Facture #{self.id} — {self.get_type_facture_display()} — {self.montantFacture}"


class Document(models.Model):
    """Document attaché à une propriété ou un utilisateur."""
    utilisateur = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name='documents')
    propriete = models.ForeignKey(
        Propriete, on_delete=models.SET_NULL, null=True, blank=True, related_name='documents')
    type_document = models.CharField(
        max_length=3, choices=TypeDocument.choices, default=TypeDocument.AUTRE)
    titre = models.CharField(max_length=150)
    fichier = models.FileField(upload_to='documents/%Y/%m/')
    date_upload = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = "Document"
        verbose_name_plural = "Documents"
        ordering = ['-date_upload']

    def __str__(self):
        return self.titre


class Contrat(models.Model):
    """Contrat de location (document signé)."""
    location = models.OneToOneField(
        Location, on_delete=models.CASCADE, related_name='contrat')
    fichier = models.FileField(upload_to='contrats/%Y/%m/')
    date_debut = models.DateField()
    date_fin = models.DateField()
    date_creation = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = "Contrat"
        verbose_name_plural = "Contrats"

    def __str__(self):
        return f"Contrat location #{self.location_id}"


class Intervention(models.Model):
    """Demande d'intervention / maintenance sur un bien."""
    propriete = models.ForeignKey(
        Propriete, on_delete=models.CASCADE, related_name='interventions')
    demandeur = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='interventions_demandees')
    titre = models.CharField(max_length=150)
    description = models.TextField()
    statut = models.CharField(max_length=3, choices=StatutIntervention.choices, default=StatutIntervention.OUVERTE)
    commentaire_proprietaire = models.TextField(blank=True)
    date_creation = models.DateTimeField(default=timezone.now)
    date_cloture = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Intervention"
        verbose_name_plural = "Interventions"
        ordering = ['-date_creation']

    def __str__(self): return f"{self.titre} — {self.propriete.designation}"
