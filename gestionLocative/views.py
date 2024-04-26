from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from dateutil.relativedelta import relativedelta
from .forms import *
from .models import *


# Create your views here.
@login_required
def payer_facture(request, location_id):
    location = Location.objects.get(id=location_id)
    if request.method == 'POST':
        montant = request.POST['montant']
        if montant == location.propriete.montant:
            facture = Facture(utilisateur=request.user, propriete=location.propriete, montantFacture=montant)
            facture.est_paye = True
            facture.save()
            messages.success(request, 'La facture a été payée avec succès.')
            return redirect('liste_locations')
        else:
            messages.error(request, 'La montant n\'est pas conforme.')
            return render(request, 'locative/payer_facture.html', {'facture': facture, 'title': 'Payer facture' })

    return render(request, 'locative/payer_facture.html', {'location': location, 'title': 'Payer facture' })

@login_required
def liste_factures(request):
    factures = Facture.objects.filter(utilisateur=request.user).values()
    return render(request, 'locative/liste_factures.html', {'factures': factures, 'title': 'liste de facture' })

@login_required
def demander_location(request, propriete_id):
    propriete = get_object_or_404(Propriete, id=propriete_id)
    if request.method == 'POST':
        date_fin = request.POST['date_fin']
        propriete.locataire = request.user
        location = Location(utilisateur=request.user, propriete=propriete, date_fin=date_fin)
        location.propriete.demande_allocation = True
        location.save()
        messages.success(request, 'La demande de location a été soumise avec succès.')
        return redirect('dashboard')
    return render(request, 'locative/demander_location.html', {'propriete': propriete, 'title': 'demande de location' })

@login_required
def liste_locations(request):
    locations = Location.objects.filter(utilisateur=request.user).values()
    return render(request, 'locative/liste_locations.html', {'locations': locations, 'title': 'liste de location' })

@login_required
def autoriser_location(request, location_id):
    location = Location.objects.get(id=location_id)
    if request.method == 'POST':
        rep = request.POST['reponse']
        if rep == 'yes':
            location.est_autorisee = True
            location.propriete.est_loue = True
            duree = relativedelta(location.date_fin, location.date_debut)
            location.montantLocation = location.propriete.montant * duree.months
            location.save()
            messages.success(request, 'La location a été autorisée avec succès.')
            return redirect('read_user_properties')
        else:
            location.propriete.demande_allocation = False
            location.propriete.n += 1
            messages.error(request, 'La location a été refutée.')
    return render(request, 'locative/autoriser_location.html', {'location': location, 'title': 'autorisation location' })

@login_required
def gerer_documents(request, propriete_id):
    documents = Document.objects.filter(utilisateur=request.user).values()
    if request.method == 'POST':
        propriete = Propriete.objects.get(id=propriete_id)
        titre = request.POST['titre']
        fichier = request.FILES['fichier']
        document = Document(utilisateur=request.user, propriete=propriete_id, titre=titre, fichier=fichier)
        document.save()
        messages.success(request, 'Le document a été téléchargé avec succès.')
        return redirect('read_user_properties')
    return render(request, 'locative/gerer_documents.html', {'documents': documents, 'propriete': propriete, 'title': 'gestion de document' })

def connexion(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Identifiants invalides.')
    return render(request, 'locative/connexion.html', { 'title': 'connexion' })

@login_required
def deconnexion(request):
    logout(request)
    return redirect('accueil')

def inscription(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        last_name = request.POST['last_name']
        email = request.POST['email']
        first_name = request.POST['first_name']
        User.objects.create_user(username=username, email=email, password=password, last_name=last_name, first_name=first_name)
        messages.success(request, 'Votre compte a été créé avec succès. Veuillez vous connecter.')
        return redirect('connexion')
    return render(request, 'locative/inscription.html', { 'title': 'INSCRIPTION' })

def accueil(request):
    propriete = Propriete.objects.filter(est_loue=False).order_by('nb_chambre').reverse()[:6].values()
    return render(request, 'locative/accueil.html', { 'title': 'accueil', 'proprietes': propriete })

@login_required
def dashboard(request):
    proprietes = Propriete.objects.exclude(proprietaire=request.user).order_by('designation').reverse()[:5].values()
    documents = Document.objects.filter(utilisateur=request.user).order_by('titre').reverse()[:5].values()
    locations = Location.objects.filter(utilisateur=request.user).order_by('date_debut').reverse()[:5].values()
    nb_doc = len(documents)
    nb_loc = len(locations)
    return render(request, 'locative/dashboard.html', {'documents': documents, 'locations': locations, 'proprietes': proprietes, 'nb_doc': nb_doc, 'nb_loc': nb_loc})

@login_required
def create_propriete(request, propriete_id):
    propriete = get_object_or_404(Propriete, id=propriete_id)
    if request.method == "POST":
        nb_etage = request.POST["nb_etage"]
        adresse = request.POST["adresse"]
        ville = request.POST["ville"]
        code_postal = request.POST["code_postal"]
        designation = request.POST["designation"]
        description = request.POST["description"]
        nb_chambre = request.POST["nb_chambre"]
        surface = request.POST["surface"]
        montant = request.POST["montant"]
        propriete = Propriete(nb_etage = nb_etage, adresse = adresse, ville = ville, designation = designation, montant = montant, code_postal = code_postal, description = description, nb_chambre = nb_chambre, surface = surface, proprietaire = propriete)
        propriete.save()
        messages.info(request, f"La propriété a bien été ajoutée.")
        return redirect("dashboard")
    else:
        form = ProprieteForm()
        messages.warning(request, "Erreur lors de l'ajout de la propriété")
    return render(request, "locative/create_propriete.html", {"form": form, "title": "Creation de propriété"})

@login_required
def read_propriete(request, propriete_id):
    propriete = get_object_or_404(Propriete, id=propriete_id)
    return render(request, 'locative/read_propriete.html', {"propriete": propriete, "title": "Propriete"})

@login_required
def read_user_properties(request):
    properties = Propriete.objects.filter(proprietaire=request.user).order_by('ville').values()
    return render(request, 'locative/user_properties.html', {'user': request.user, 'proprietes': properties, "title": "Mes Proprietes"})

@login_required
def read_properties_dispo(request):
    properties = Propriete.objects.filter(est_loue=False).order_by('ville').values()
    return render(request, 'locative/user_dispo_properties.html', {'proprietes': properties, "title": "Proprietes non alouees"})

@login_required
def read_all_propriete(request):
    proprietes = Propriete.objects.all().order_by('propriete.username').values().distinct()
    return render(request, "locative/read_all_propriete", {"proprietes": proprietes, "title": "Liste des propriétés"})

@login_required
def update_propriete(request, propriete_id):
    propriete = get_object_or_404(Propriete, id=propriete_id)
    if request.method == 'POST':
        form = ProprieteForm(instance=propriete, data=request.POST)
        if form.is_valid():
            propriete = form.save()
            propriete.utilisateur = request.user
            propriete.save()
            return redirect('read_propriete', propriete_id=propriete.id)
    propriete = get_object_or_404(Propriete, id=propriete_id)
    return render(request, "locative/modifier_produit.html", {"propriete": propriete, "title": "Modification d'une propriete"})

@login_required
def delete_propriete(request, propriete_id):
    propriete = get_object_or_404(Propriete, id=propriete_id)
    propriete.delete()
    messages.error(request, f"La propriété a bien été supprimée.")
    return redirect('read_user_properties')