# Generated manually for plateforme locative complète

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('gestionLocative', '0002_rename_montant_facture_montantfacture_and_more'),
    ]

    operations = [
        # Propriete: nouveaux champs
        migrations.AddField(
            model_name='propriete',
            name='type_propriete',
            field=models.CharField(choices=[('APP', 'Appartement'), ('MAI', 'Maison'), ('STU', 'Studio'), ('LOC', 'Local commercial'), ('AUT', 'Autre')], default='APP', max_length=3),
        ),
        migrations.AddField(
            model_name='propriete',
            name='complement_adresse',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='propriete',
            name='charges_comprises',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='propriete',
            name='montant_charges',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=8),
        ),
        migrations.AddField(
            model_name='propriete',
            name='garantie',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='propriete',
            name='statut',
            field=models.CharField(choices=[('DIS', 'Disponible'), ('LOU', 'Loué'), ('MAI', 'En maintenance'), ('RES', 'Réservé')], default='DIS', max_length=3),
        ),
        migrations.AddField(
            model_name='propriete',
            name='photo',
            field=models.ImageField(blank=True, null=True, upload_to='proprietes/'),
        ),
        migrations.AddField(
            model_name='propriete',
            name='date_creation',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='propriete',
            name='date_modification',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='propriete',
            name='designation',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='propriete',
            name='adresse',
            field=models.CharField(max_length=200),
        ),
        migrations.AlterField(
            model_name='propriete',
            name='ville',
            field=models.CharField(max_length=80),
        ),
        # Location
        migrations.AddField(
            model_name='location',
            name='statut',
            field=models.CharField(choices=[('ATT', 'En attente'), ('ACC', 'Acceptée'), ('REF', 'Refusée'), ('TER', 'Terminée')], default='ATT', max_length=3),
        ),
        migrations.AddField(
            model_name='location',
            name='motif_refus',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='location',
            name='date_reponse',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='location',
            name='message_demande',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='location',
            name='date_creation',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='location',
            name='montantLocation',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12),
        ),
        # Facture
        migrations.AddField(
            model_name='facture',
            name='location',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='factures', to='gestionLocative.location'),
        ),
        migrations.AddField(
            model_name='facture',
            name='type_facture',
            field=models.CharField(choices=[('LOY', 'Loyer'), ('CHA', 'Charges'), ('REG', 'Régularisation'), ('AUT', 'Autre')], default='LOY', max_length=3),
        ),
        migrations.AddField(
            model_name='facture',
            name='date_echeance',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='facture',
            name='date_paiement',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='facture',
            name='periode',
            field=models.CharField(blank=True, max_length=7),
        ),
        migrations.AddField(
            model_name='facture',
            name='reference',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='facture',
            name='date_creation',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        # Document
        migrations.AddField(
            model_name='document',
            name='type_document',
            field=models.CharField(choices=[('CON', 'Contrat de location'), ('IDE', 'Pièce d\'identité'), ('JUS', 'Justificatif de domicile'), ('AUT', 'Autre')], default='AUT', max_length=3),
        ),
        migrations.AddField(
            model_name='document',
            name='date_upload',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        # Contrat
        migrations.CreateModel(
            name='Contrat',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fichier', models.FileField(upload_to='contrats/%Y/%m/')),
                ('date_debut', models.DateField()),
                ('date_fin', models.DateField()),
                ('date_creation', models.DateTimeField(default=django.utils.timezone.now)),
                ('location', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='contrat', to='gestionLocative.location')),
            ],
            options={
                'verbose_name': 'Contrat',
                'verbose_name_plural': 'Contrats',
            },
        ),
        # Intervention
        migrations.CreateModel(
            name='Intervention',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titre', models.CharField(max_length=150)),
                ('description', models.TextField()),
                ('statut', models.CharField(choices=[('OUV', 'Ouverte'), ('COU', 'En cours'), ('CLO', 'Clôturée')], default='OUV', max_length=3)),
                ('commentaire_proprietaire', models.TextField(blank=True)),
                ('date_creation', models.DateTimeField(default=django.utils.timezone.now)),
                ('date_cloture', models.DateTimeField(blank=True, null=True)),
                ('demandeur', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='interventions_demandees', to=settings.AUTH_USER_MODEL)),
                ('propriete', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='interventions', to='gestionLocative.propriete')),
            ],
            options={
                'verbose_name': 'Intervention',
                'verbose_name_plural': 'Interventions',
                'ordering': ['-date_creation'],
            },
        ),
    ]
