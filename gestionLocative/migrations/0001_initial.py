# Generated by Django 4.2.7 on 2024-01-24 01:12

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Propriete',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nb_etage', models.CharField(max_length=20)),
                ('adresse', models.CharField(max_length=50)),
                ('designation', models.CharField(max_length=50)),
                ('ville', models.CharField(blank=True, max_length=20)),
                ('code_postal', models.CharField(blank=True, max_length=20)),
                ('description', models.TextField(blank=True)),
                ('nb_chambre', models.PositiveSmallIntegerField()),
                ('surface', models.DecimalField(decimal_places=2, max_digits=6)),
                ('montant', models.DecimalField(decimal_places=2, max_digits=15)),
                ('est_loue', models.BooleanField(default=False)),
                ('locataire', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='locataire', to=settings.AUTH_USER_MODEL)),
                ('proprietaire', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='proprietaire', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_debut', models.DateField(auto_now_add=True)),
                ('date_fin', models.DateField()),
                ('est_autorisee', models.BooleanField(default=False)),
                ('propriete', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='propriete_loc', to='gestionLocative.propriete')),
                ('utilisateur', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='propriete_loc', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Facture',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('montant', models.DecimalField(decimal_places=2, max_digits=8)),
                ('date_facturation', models.DateField(auto_now_add=True)),
                ('est_paye', models.BooleanField(default=False)),
                ('propriete', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gestionLocative.propriete')),
                ('utilisateur', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titre', models.CharField(max_length=100)),
                ('fichier', models.FileField(upload_to='documents/')),
                ('propriete', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='propriete_doc', to='gestionLocative.propriete')),
                ('utilisateur', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='utilisateur_doc', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
