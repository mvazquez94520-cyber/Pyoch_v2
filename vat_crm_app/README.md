# CRM de Gestion de TVA

Ce CRM (Customer Relationship Management) est spécifiquement conçu pour aider les entreprises à gérer leur TVA (Taxe sur la Valeur Ajoutée). L'application offre les fonctionnalités suivantes :

## Fonctionnalités principales

- **Saisie manuelle** : Ajouter des documents fiscaux avec les informations essentielles
- **Lecture de PDF** : Extraire automatiquement les données des factures PDF
- **Calcul automatique** : Calcul des montants HT, TVA et TTC
- **Export Excel** : Génération d'un fichier Excel avec les données structurées
- **Interface web** : Interface utilisateur conviviale en français

## Champs gérés

L'application gère les champs suivants :
- **Nomination** : Libellé de la dépense
- **Montant HT** : Montant Hors Taxe
- **TVA** : Taux de TVA et montant de TVA
- **Montant TTC** : Montant Total Toutes Taxes Comprises
- **Date** : Date de la transaction
- **Fournisseur** : Nom du fournisseur
- **Numéro de facture** : Numéro de la facture

## Installation et lancement

1. Installez les dépendances :
   ```bash
   pip install -r requirements.txt
   ```

2. Lancez l'application :
   ```bash
   python main.py
   ```

3. Accédez à l'interface web à l'adresse : http://localhost:8080

## Utilisation

### Ajout manuel d'un document
1. Remplissez les champs du formulaire (nomination, montant HT, taux de TVA, etc.)
2. Cliquez sur "Ajouter le document"
3. Le montant de TVA et le montant TTC seront calculés automatiquement

### Lecture d'un PDF de facture
1. Téléchargez un fichier PDF de facture dans la section "Lecture de PDF de facture"
2. Cliquez sur "Lire le PDF"
3. Les informations extraites du PDF seront automatiquement remplies dans le formulaire

### Export vers Excel
1. Cliquez sur le bouton "Exporter vers Excel"
2. Le fichier Excel contenant toutes les données sera téléchargé

## API Endpoints

- `GET /` : Interface web principale
- `POST /api/records` : Ajouter un nouveau document TVA
- `GET /api/records` : Obtenir tous les documents TVA
- `GET /api/export-excel` : Exporter les données vers Excel
- `POST /api/process-pdf` : Traiter un fichier PDF pour extraction de données

## Structure du projet

```
vat_crm_app/
├── main.py          # Application principale
├── requirements.txt # Dépendances
├── uploads/         # Fichiers PDF temporaires
└── excel_exports/   # Fichiers Excel exportés
```

## Technologies utilisées

- **FastAPI** : Framework web pour la création de l'API
- **Pandas** : Manipulation et export des données vers Excel
- **PDFMiner** : Extraction de texte à partir des fichiers PDF
- **OpenPyXL** : Génération de fichiers Excel
- **HTML/CSS/JavaScript** : Interface utilisateur

## Cas d'utilisation

Cette application est idéale pour :
- Les petites et moyennes entreprises qui doivent gérer leur TVA
- Les comptables qui doivent traiter des factures fournisseurs
- Les services financiers qui doivent suivre les obligations fiscales
- Toute organisation qui doit conserver un historique des charges avec détails TVA