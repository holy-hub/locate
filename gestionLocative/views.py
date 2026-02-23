from decimal import Decimal
from datetime import date, timedelta
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Sum, Q
from django.utils import timezone
from dateutil.relativedelta import relativedelta

from .forms import *
from .models import (
    Propriete, Location, Facture, Document, Contrat, Intervention, User,
    TypePropriete, StatutPropriete, StatutLocation, TypeFacture, TypeDocument, StatutIntervention,)

# --- Auth & pages publiques ---

def accueil(request):
    """Page d'accueil avec biens disponibles et filtres."""
    qs = Propriete.objects.filter(
        statut=StatutPropriete.DISPONIBLE,
        est_loue=False
    ).select_related('proprietaire').order_by('-date_creation')

    ville = request.GET.get('ville', '').strip()
    if ville:
        qs = qs.filter(ville__icontains=ville)
    type_p = request.GET.get('type')
    if type_p and type_p in dict(TypePropriete.choices):
        qs = qs.filter(type_propriete=type_p)
    try:
        prix_min = request.GET.get('prix_min')
        if prix_min:
            qs = qs.filter(montant__gte=Decimal(prix_min))
    except Exception:
        pass
    try:
        prix_max = request.GET.get('prix_max')
        if prix_max:
            qs = qs.filter(montant__lte=Decimal(prix_max))
    except Exception:
        pass

    proprietes = qs[:12]
    return render(request, 'locative/accueil.html', {
        'title': 'Accueil',
        'proprietes': proprietes,
        'filtres': {'ville': ville, 'type': type_p, 'prix_min': request.GET.get('prix_min'), 'prix_max': request.GET.get('prix_max')},
    })

def connexion(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next') or 'dashboard'
            return redirect(next_url)
        messages.error(request, 'Identifiants invalides.')
    return render(request, 'locative/connexion.html', {'title': 'Connexion'})

def inscription(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        email = request.POST.get('email', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        role = request.POST.get('role', '').strip()

        if not username or not password:
            messages.error(request, 'Identifiant et mot de passe requis.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Ce nom d\'utilisateur est déjà pris.')
        else:
            user = User.objects.create_user(
                username=username,
                email=email or '',
                password=password,
                first_name=first_name,
                last_name=last_name,)
            role_val = role if role in (User.ROLE_PROPRIO, User.ROLE_LOCA) else User.ROLE_LOCA
            User.objects.create(user=user, role=role_val)
            messages.success(request, 'Compte créé. Connectez-vous.')
            return redirect('connexion')
    return render(request, 'locative/inscription.html', {
        'title': 'Inscription',
        'role_choices': User.ROLE_CHOICES,})

@login_required
def deconnexion(request):
    try: logout(request)
    except(ValueError, TypeError): logout(request)
    return redirect('accueil')

# --- Dashboard ---

@login_required
def dashboard(request):
    """Tableau de bord avec statistiques et aperçus."""
    # Propriétés à louer (hors les miennes)
    proprietes_dispo = list(
        Propriete.objects.exclude(proprietaire=request.user)
        .filter(est_loue=False, statut=StatutPropriete.DISPONIBLE)
        .select_related('proprietaire').order_by('-date_creation')[:5]
    )
    documents = list(
        Document.objects.filter(utilisateur=request.user, propriete__isnull=False)
        .select_related('propriete').order_by('-date_upload')[:5]
    )
    locations = list(
        Location.objects.filter(utilisateur=request.user)
        .select_related('propriete', 'utilisateur')
        .order_by('-date_creation')[:5]
    )

    # Stats propriétaire
    mes_proprietes = Propriete.objects.filter(proprietaire=request.user)
    nb_proprietes = mes_proprietes.count()
    locations_actives = Location.objects.filter(
        propriete__proprietaire=request.user,
        est_autorisee=True,
        date_fin__gte=date.today()
    )
    nb_locations_actives = locations_actives.count()
    revenus_mois = Facture.objects.filter(
        propriete__proprietaire=request.user,
        type_facture=TypeFacture.LOYER,
        date_facturation__year=date.today().year,
        date_facturation__month=date.today().month,
        est_paye=True
    ).aggregate(s=Sum('montantFacture'))['s'] or Decimal('0')

    return render(request, 'locative/dashboard.html', {
        'title': 'Tableau de bord',
        'documents': documents,
        'locations': locations,
        'proprietes': proprietes_dispo,
        'nb_doc': len(documents),
        'nb_loc': len(locations),
        'nb_proprietes': nb_proprietes,
        'nb_locations_actives': nb_locations_actives,
        'revenus_mois': revenus_mois,
    })

# --- Propriétés (CRUD) ---

@login_required
def create_propriete(request, user_id):
    if request.user.id != user_id:
        messages.error(request, 'Action non autorisée.')
        return redirect('dashboard')
    if request.method == 'POST':
        designation = request.POST.get('designation', '').strip()
        adresse = request.POST.get('adresse', '').strip()
        ville = request.POST.get('ville', '').strip()
        nb_etage = request.POST.get('nb_etage', '').strip()
        nb_chambre = request.POST.get('nb_chambre')
        surface = request.POST.get('surface')
        montant = request.POST.get('montant')
        code_postal = request.POST.get('code_postal', '').strip()
        description = request.POST.get('description', '').strip()
        type_val = request.POST.get('type_propriete', '').strip()
        statut_val = request.POST.get('statut_propriete', '').strip()

        if type_val not in dict(TypePropriete.choices):
            type_val = TypePropriete.APPARTEMENT

        if statut_val not in dict(TypePropriete.choices):
            statut_val = StatutPropriete.DISPONIBLE

        if designation and adresse and ville and nb_chambre and surface and montant:
            try:
                p = Propriete(
                    type_propriete=type_val,
                    statut=statut_val,
                    designation=designation,
                    description=description,
                    adresse=adresse,
                    code_postal=code_postal,
                    ville=ville,
                    nb_etage=nb_etage,
                    nb_chambre=int(nb_chambre),
                    surface=Decimal(str(surface)),
                    montant=Decimal(str(montant)),
                    proprietaire=request.user,)
                if request.FILES.get('photo'):
                    p.photo = request.FILES['photo']
                p.save()
                messages.success(request, 'Propriété créée.')
                return redirect('read_user_properties')
            except (ValueError, TypeError):
                messages.warning(request, 'Valeurs invalides (nombre ou date).')
        else:
            messages.warning(request, 'Remplissez tous les champs obligatoires.')
    return render(request, 'locative/create_propriete.html', {
        'title': 'Création de propriété',
        'type_propriete_choices': TypePropriete.choices,
        'statut_propriete_choices': StatutPropriete.choices, 
    })

@login_required
def read_propriete(request, propriete_id):
    propriete = get_object_or_404(Propriete.objects.select_related('proprietaire', 'locataire'), id=propriete_id)
    # Voir si l'utilisateur est propriétaire ou locataire pour afficher actions
    est_proprietaire = propriete.proprietaire_id == request.user.id
    est_locataire = propriete.locataire_id == request.user.id
    return render(request, 'locative/read_propriete.html', {
        'propriete': propriete,
        'title': propriete.designation,
        'est_proprietaire': est_proprietaire,
        'est_locataire': est_locataire,
    })

@login_required
def read_user_properties(request):
    proprietes = Propriete.objects.filter(proprietaire=request.user).order_by('ville', 'designation')
    locations_en_attente = Location.objects.filter(
        propriete__proprietaire=request.user,
        statut=StatutLocation.EN_ATTENTE
    ).select_related('propriete', 'utilisateur')
    return render(request, 'locative/user_properties.html', {
        'user': request.user,
        'proprietes': proprietes,
        'locations_en_attente': locations_en_attente,
        'title': 'Mes propriétés',
    })

@login_required
def read_properties_dispo(request):
    qs = Propriete.objects.filter(est_loue=False, statut=StatutPropriete.DISPONIBLE).select_related('proprietaire')
    ville = request.GET.get('ville', '').strip()
    if ville: qs = qs.filter(ville__icontains=ville)
    paginator = Paginator(qs.order_by('ville'), 12)
    page = request.GET.get('page', 1)
    proprietes = paginator.get_page(page)
    return render(request, 'locative/user_dispo_properties.html', {
        'proprietes': proprietes, 
        'title': 'Propriétés disponibles',})

@login_required
def read_all_propriete(request):
    qs = Propriete.objects.all().select_related('proprietaire').order_by('proprietaire__username', 'ville')
    paginator = Paginator(qs, 20)
    page = request.GET.get('page', 1)
    proprietes = paginator.get_page(page)
    return render(request, 'locative/read_all_propriete.html', {
        'proprietes': proprietes,
        'title': 'Toutes les propriétés',})

@login_required
def update_propriete(request, propriete_id):
    propriete = get_object_or_404(Propriete, id=propriete_id)
    if propriete.proprietaire_id != request.user.id:
        messages.error(request, 'Action non autorisée.')
        return redirect('read_user_properties')
    if request.method == 'POST':
        propriete.designation = request.POST.get('designation', '').strip() or propriete.designation
        propriete.adresse = request.POST.get('adresse', '').strip() or propriete.adresse
        propriete.ville = request.POST.get('ville', '').strip() or propriete.ville
        propriete.code_postal = request.POST.get('code_postal', '').strip() or propriete.code_postal
        propriete.description = request.POST.get('description', '').strip() or propriete.description
        propriete.nb_etage = request.POST.get('nb_etage', '').strip() or propriete.nb_etage
        propriete.type_propriete = request.POST.get('type_propriete', '').strip() or propriete.type_propriete
        propriete.statut = request.POST.get('statut_propriete', '').strip() or propriete.statut
        try:
            propriete.nb_chambre = int(request.POST.get('nb_chambre') or propriete.nb_chambre)
            propriete.surface = Decimal(request.POST.get('surface') or propriete.surface)
            propriete.montant = Decimal(request.POST.get('montant') or propriete.montant)
        except (TypeError, ValueError):
            messages.warning(request, 'Valeurs numériques invalides.')
            return render(request, 'locative/modifier_produit.html', {'propriete': propriete, 'title': 'Modifier la propriété'})
        if request.FILES.get('photo'):
            propriete.photo = request.FILES['photo']
        propriete.save()
        messages.success(request, 'Propriété mise à jour.')
        return redirect('read_propriete', propriete_id=propriete.id)
    return render(request, 'locative/modifier_produit.html', {
        'propriete': propriete,
        'title': 'Modifier la propriété',
        'type_propriete_choices': TypePropriete.choices,
        'statut_propriete_choices': StatutPropriete.choices,})


@login_required
def delete_propriete(request, propriete_id):
    propriete = get_object_or_404(Propriete, id=propriete_id)
    if propriete.proprietaire_id != request.user.id:
        messages.error(request, 'Action non autorisée.')
        return redirect('read_user_properties')
    propriete.delete()
    messages.success(request, 'Propriété supprimée.')
    return redirect('read_user_properties')


# --- Locations (demande, autorisation, liste) ---

@login_required
def demander_location(request, propriete_id):
    propriete = get_object_or_404(Propriete, id=propriete_id)
    if propriete.est_loue or propriete.statut != StatutPropriete.DISPONIBLE:
        messages.warning(request, 'Ce bien n\'est plus disponible.')
        return redirect('dashboard')
    if request.method == 'POST':
        date_fin_str = request.POST.get('date_fin')
        message_demande = request.POST.get('message_demande', '').strip()
        if not date_fin_str:
            messages.error(request, 'La date de fin est requise.')
        else:
            try:
                date_fin = date.fromisoformat(date_fin_str)
                if date_fin <= date.today():
                    messages.error(request, 'La date de fin doit être ultérieure à aujourd\'hui.')
                else:
                    propriete.demande_allocation = True
                    propriete.locataire = request.user
                    propriete.save()
                    loc = Location(
                        utilisateur=request.user,
                        propriete=propriete,
                        date_fin=date_fin,
                        message_demande=message_demande or '',
                        statut=StatutLocation.EN_ATTENTE,
                    )
                    loc.save()
                    messages.success(request, 'Demande envoyée.')
                    return redirect('dashboard')
            except ValueError:
                messages.error(request, 'Date invalide.')
    return render(request, 'locative/demander_location.html', {
        'propriete': propriete,
        'title': 'Demande de location',
    })


@login_required
def autoriser_location(request, location_id):
    location = get_object_or_404(
        Location.objects.select_related('propriete', 'utilisateur'),
        id=location_id
    )
    if location.propriete.proprietaire_id != request.user.id:
        messages.error(request, 'Action non autorisée.')
        return redirect('read_user_properties')
    if location.statut != StatutLocation.EN_ATTENTE:
        messages.info(request, 'Cette demande a déjà été traitée.')
        return redirect('read_user_properties')

    if request.method == 'POST':
        rep = request.POST.get('reponse')
        if rep == 'yes':
            location.est_autorisee = True
            location.statut = StatutLocation.ACCEPTEE
            location.date_reponse = timezone.now()
            # Montant total sur la durée
            duree = relativedelta(location.date_fin, location.date_debut)
            nb_mois = max(1, duree.months + 12 * duree.years)
            location.montantLocation = location.propriete.loyer_total() * nb_mois
            location.save()

            propriete = location.propriete
            propriete.est_loue = True
            propriete.statut = StatutPropriete.LOUE
            propriete.demande_allocation = False
            propriete.save()

            messages.success(request, 'Location acceptée.')
        else:
            motif = request.POST.get('motif_refus', '').strip()
            location.statut = StatutLocation.REFUSEE
            location.motif_refus = motif or 'Refusée par le propriétaire'
            location.date_reponse = timezone.now()
            location.save()

            propriete = location.propriete
            propriete.demande_allocation = False
            propriete.n = (propriete.n or 0) + 1
            propriete.locataire = None
            propriete.save()
            messages.info(request, 'Demande refusée.')
        return redirect('read_user_properties')

    return render(request, 'locative/autoriser_location.html', {
        'location': location,
        'title': 'Autoriser / Refuser la location',
    })


@login_required
def liste_locations(request):
    locations = (
        Location.objects.filter(utilisateur=request.user)
        .select_related('propriete', 'utilisateur')
        .order_by('-date_creation')
    )
    return render(request, 'locative/liste_locations.html', {
        'locations': locations,
        'title': 'Mes locations',
    })


# --- Factures ---

@login_required
def liste_factures(request):
    factures = (
        Facture.objects.filter(utilisateur=request.user)
        .select_related('propriete', 'location')
        .order_by('-date_facturation')
    )
    total_impaye = factures.filter(est_paye=False).aggregate(s=Sum('montantFacture'))['s'] or Decimal('0')
    return render(request, 'locative/liste_factures.html', {
        'factures': factures,
        'total_impaye': total_impaye,
        'title': 'Mes factures',
    })


@login_required
def payer_facture(request, location_id):
    location = get_object_or_404(
        Location.objects.select_related('propriete'),
        id=location_id,
        utilisateur=request.user
    )
    if not location.est_autorisee or not location.propriete:
        messages.error(request, 'Location invalide.')
        return redirect('liste_locations')

    montant_attendu = location.propriete.loyer_total()
    if request.method == 'POST':
        try:
            montant = Decimal(request.POST.get('montant', 0))
        except Exception:
            montant = Decimal('0')
        if montant == montant_attendu:
            facture = Facture(
                utilisateur=request.user,
                propriete=location.propriete,
                location=location,
                type_facture=TypeFacture.LOYER,
                montantFacture=montant,
                est_paye=True,
                date_paiement=date.today(),
                periode=date.today().strftime('%Y-%m'),
            )
            facture.save()
            messages.success(request, 'Paiement enregistré.')
            return redirect('liste_locations')
        messages.error(request, 'Le montant ne correspond pas au loyer.')
    return render(request, 'locative/payer_facture.html', {
        'location': location,
        'montant_attendu': montant_attendu,
        'title': 'Payer le loyer',
    })


@login_required
def generer_facture_mois(request, location_id):
    """Génère une facture de loyer pour le mois en cours (propriétaire)."""
    location = get_object_or_404(
        Location.objects.select_related('propriete'),
        id=location_id
    )
    if location.propriete.proprietaire_id != request.user.id:
        messages.error(request, 'Action non autorisée.')
        return redirect('read_user_properties')
    if not location.est_autorisee:
        messages.warning(request, 'Location non active.')
        return redirect('read_user_properties')

    mois = date.today()
    periode = mois.strftime('%Y-%m')
    existe = Facture.objects.filter(
        location=location, type_facture=TypeFacture.LOYER, periode=periode
    ).exists()
    if existe:
        messages.info(request, 'Une facture existe déjà pour ce mois.')
        return redirect('read_user_properties')

    montant = location.propriete.loyer_total()
    echeance = date(mois.year, mois.month, 1) + timedelta(days=30)
    Facture.objects.create(
        utilisateur=location.utilisateur,
        propriete=location.propriete,
        location=location,
        type_facture=TypeFacture.LOYER,
        montantFacture=montant,
        date_echeance=echeance,
        periode=periode,
    )
    messages.success(request, f'Facture {periode} créée.')
    return redirect('read_user_properties')


# --- Documents ---

@login_required
def gerer_documents(request, propriete_id):
    propriete = get_object_or_404(Propriete, id=propriete_id)
    if propriete.proprietaire_id != request.user.id:
        messages.error(request, 'Action non autorisée.')
        return redirect('read_user_properties')

    documents = Document.objects.filter(propriete=propriete).order_by('-date_upload')
    if request.method == 'POST':
        titre = request.POST.get('titre', '').strip()
        fichier = request.FILES.get('fichier')
        type_doc = request.POST.get('type_document', TypeDocument.AUTRE)
        if titre and fichier:
            if type_doc not in dict(TypeDocument.choices):
                type_doc = TypeDocument.AUTRE
            Document.objects.create(
                utilisateur=request.user,
                propriete=propriete,
                titre=titre,
                fichier=fichier,
                type_document=type_doc,
            )
            messages.success(request, 'Document ajouté.')
            return redirect('gerer_documents', propriete_id=propriete.id)
        messages.warning(request, 'Titre et fichier requis.')
    return render(request, 'locative/gerer_documents.html', {
        'documents': documents,
        'propriete': propriete,
        'title': 'Documents',
    })

# --- Interventions (maintenance) ---

@login_required
def liste_interventions(request):
    # Propriétaire : interventions sur ses biens ; Locataire : interventions qu'il a demandées
    interventions_proprio = Intervention.objects.filter(
        propriete__proprietaire=request.user
    ).select_related('propriete', 'demandeur').order_by('-date_creation')
    interventions_loc = Intervention.objects.filter(
        demandeur=request.user
    ).select_related('propriete').order_by('-date_creation')
    return render(request, 'locative/liste_interventions.html', {
        'interventions_proprio': interventions_proprio,
        'interventions_loc': interventions_loc,
        'title': 'Interventions',
    })

@login_required
def creer_intervention(request, propriete_id):
    propriete = get_object_or_404(Propriete, id=propriete_id)
    # Seul le locataire ou le propriétaire peut créer une intervention
    if propriete.locataire_id != request.user.id and propriete.proprietaire_id != request.user.id:
        messages.error(request, 'Action non autorisée.')
        return redirect('dashboard')

    if request.method == 'POST':
        titre = request.POST.get('titre', '').strip()
        description = request.POST.get('description', '').strip()
        if titre and description:
            Intervention.objects.create(
                propriete=propriete,
                demandeur=request.user,
                titre=titre,
                description=description,
                statut=StatutIntervention.OUVERTE,
            )
            messages.success(request, 'Demande d\'intervention enregistrée.')
            return redirect('liste_interventions')
        messages.warning(request, 'Titre et description requis.')
    return render(request, 'locative/creer_intervention.html', {
        'propriete': propriete,
        'title': 'Signaler un problème',
    })

@login_required
def modifier_statut_intervention(request, intervention_id):
    intervention = get_object_or_404(Intervention.objects.select_related('propriete'), id=intervention_id)
    if intervention.propriete.proprietaire_id != request.user.id:
        messages.error(request, 'Action non autorisée.')
        return redirect('liste_interventions')

    nouveau_statut = request.POST.get('statut')
    if nouveau_statut in dict(StatutIntervention.choices):
        intervention.statut = nouveau_statut
        if request.POST.get('commentaire_proprietaire'):
            intervention.commentaire_proprietaire = request.POST.get('commentaire_proprietaire', '')
        if nouveau_statut == StatutIntervention.CLOTUREE:
            intervention.date_cloture = timezone.now()
        intervention.save()
        messages.success(request, 'Statut mis à jour.')
    return redirect('liste_interventions')