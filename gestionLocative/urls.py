from django.urls import path
from .views import *

urlpatterns = [
    path('', accueil, name='accueil'),
    path('locative/user/dashboard/', dashboard, name='dashboard'),
    path('locative/user/connexion/', connexion, name='connexion'),
    path('locative/user/inscription/', inscription, name='inscription'),
    path('locative/user/deconnexion/', deconnexion, name='deconnexion'),
    path('locative/facture/payer/numero7a64<int:location_id>/sd45Bbdj/', payer_facture, name='payer_facture'),
    path('locative/facture/liste/', liste_factures, name='liste_factures'),
    path('locative/locations/liste/', liste_locations, name='liste_locations'),
    path('locative/location/demande/alloue0023sdfj<int:propriete_id>/dfjMSjd984ifh/', demander_location, name='demander_location'),
    path('locative/location/autorisation/alloue002fjd984j<int:propriete_id>/dfjM3sdSifh/', autoriser_location, name='autoriser_location'),
    path('locative/gestion/documents/doc00jg87n<int:propriete_id>/jDrhdJI47jf/', gerer_documents, name='gerer_documents'),
    path('locative/propriete/create/jsdh8esde<int:propriete_id>jdnif789refwu989/', create_propriete, name='create_propriete'),
    path('locative/propriete/read/appartement4Fu78<int:propriete_id>/36lgWMf/', read_propriete, name='read_propriete'),
    path('locative/propriete/read/one/appartement4FgWM/3lfu786/', read_user_properties, name='read_user_properties'),
    path('locative/propriete/read/dispo/appartement4fu7FgW/3lM86/', read_properties_dispo, name='read_properties_dispo'),
    path('locative/propriete/read/all/appartement4F3fu7lgWM86/', read_all_propriete, name='read_all_propriete'),
    path('locative/propriete/update/appartement4F3fu<int:propriete_id>/78lgWM6/', update_propriete, name='update_propriete'),
    path('locative/propriete/delete/appartement4FMfu<int:propriete_id>/g3Wl786/', delete_propriete, name='delete_propriete'),
]