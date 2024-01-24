from django.urls import path
from . import views

urlpatterns = [
    path('', views.accueil, name='accueil'),
    path('locative/user/dashboard/', views.dashboard, name='dashboard'),
    path('locative/user/connexion/', views.connexion, name='connexion'),
    path('locative/user/inscription/', views.inscription, name='inscription'),
    path('locative/user/deconnexion/', views.deconnexion, name='deconnexion'),
    path('locative/facture/payer/numero7a64<int:location_id>/sd45Bbdj/', views.payer_facture, name='payer_facture'),
    path('locative/facture/liste/', views.liste_factures, name='liste_factures'),
    path('locative/locations/liste/', views.liste_locations, name='liste_locations'),
    path('locative/location/demande/alloue0023sdfj<int:propriete_id>/dfjMSjd984ifh/', views.demander_location, name='demander_location'),
    path('locative/location/autorisation/alloue002fjd984j<int:propriete_id>/dfjM3sdSifh/', views.autoriser_location, name='autoriser_location'),
    path('locative/gestion/documents/doc00jg87n<int:propriete_id>/jDrhdJI47jf/', views.gerer_documents, name='gerer_documents'),
    path('locative/propriete/create/', views.create_propriete, name='create_propriete'),
    path('locative/propriete/read/appartement4Fu78<int:propriete_id>/36lgWMf/', views.read_propriete, name='read_propriete'),
    path('locative/propriete/read/one/appartement4FgWM/3lfu786/', views.read_user_properties, name='read_user_properties'),
    path('locative/propriete/read/dispo/appartement4fu7FgW/3lM86/', views.read_properties_dispo, name='read_properties_dispo'),
    path('locative/propriete/read/all/appartement4F3fu7lgWM86/', views.read_all_propriete, name='read_all_propriete'),
    path('locative/propriete/update/appartement4F3fu<int:propriete_id>/78lgWM6/', views.update_propriete, name='update_propriete'),
    path('locative/propriete/delete/appartement4FMfu<int:propriete_id>/g3Wl786/', views.delete_propriete, name='delete_propriete'),
]