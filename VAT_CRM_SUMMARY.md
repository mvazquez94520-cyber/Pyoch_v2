# CRM de Gestion de TVA - Résumé du Projet

## Description
Ce projet implémente un CRM (Customer Relationship Management) spécifiquement conçu pour aider les entreprises à gérer leur TVA (Taxe sur la Valeur Ajoutée). L'application offre une solution complète pour la gestion des factures, y compris la lecture de PDF et l'exportation Excel.

## Fonctionnalités implémentées

### 1. Interface Web
- Interface utilisateur entièrement en français
- Formulaire pour l'ajout manuel de documents fiscaux
- Affichage des enregistrements existants dans un tableau

### 2. Gestion des données TVA
- **Nomination** : Libellé de la dépense
- **Montant HT** : Montant Hors Taxe
- **TVA** : Taux de TVA et calcul automatique du montant de TVA
- **Montant TTC** : Montant Total Toutes Taxes Comprises (calculé automatiquement)
- **Date** : Date de la transaction
- **Fournisseur** : Nom du fournisseur
- **Numéro de facture** : Numéro de la facture

### 3. Lecture de PDF
- Extraction automatique des données des factures PDF
- Utilisation de PDFMiner pour l'extraction de texte
- Remplissage automatique du formulaire avec les données extraites

### 4. Export Excel
- Génération d'un fichier Excel contenant toutes les données
- Formatage automatique des colonnes
- Noms de fichiers avec horodatage

## Structure du projet

```
vat_crm_app/
├── main.py              # Application principale avec FastAPI
├── requirements.txt     # Dépendances Python
├── README.md           # Documentation du projet
├── create_sample_invoice.py  # Script de création de facture test
├── uploads/            # Répertoire pour les fichiers PDF temporaires
├── excel_exports/      # Répertoire pour les fichiers Excel exportés
├── sample_invoice.pdf  # Exemple de facture PDF
└── test_export.xlsx    # Exemple d'export Excel
```

## Technologies utilisées

- **FastAPI** : Framework web pour la création de l'API
- **Uvicorn** : Serveur ASGI pour le déploiement
- **Pandas** : Manipulation des données et export Excel
- **OpenPyXL** : Génération de fichiers Excel
- **PDFMiner** : Extraction de texte à partir des fichiers PDF
- **HTML/CSS/JavaScript** : Interface utilisateur côté client

## API Endpoints

- `GET /` : Interface web principale
- `POST /api/records` : Ajouter un nouveau document TVA
- `GET /api/records` : Obtenir tous les documents TVA
- `GET /api/export-excel` : Exporter les données vers Excel
- `POST /api/process-pdf` : Traiter un fichier PDF pour extraction de données

## Installation et déploiement

1. Naviguez vers le répertoire du projet :
   ```bash
   cd /workspace/vat_crm_app
   ```

2. Installez les dépendances :
   ```bash
   pip install -r requirements.txt
   ```

3. Lancez l'application :
   ```bash
   python main.py
   ```

4. Accédez à l'interface web à l'adresse : http://localhost:8080

## Tests effectués

- ✅ Démarrage de l'application sur le port 8080
- ✅ Ajout manuel de documents TVA via l'API
- ✅ Récupération des documents existants
- ✅ Traitement de fichiers PDF avec extraction de données
- ✅ Exportation vers Excel avec formatage approprié
- ✅ Interface web entièrement fonctionnelle

## Points forts

1. **Interface utilisateur intuitive** : Entièrement en français avec un design clair
2. **Calcul automatique** : Les montants TVA et TTC sont calculés automatiquement
3. **Intégration PDF** : Capacité à lire et extraire des données des factures PDF
4. **Export Excel** : Formatage automatique des colonnes dans les exports
5. **API complète** : Endpoints pour toutes les fonctionnalités
6. **Sécurité** : Toutes les données restent locales

## Cas d'utilisation

Cette application est idéale pour :
- Les petites et moyennes entreprises qui doivent gérer leur TVA
- Les comptables qui doivent traiter des factures fournisseurs
- Les services financiers qui doivent suivre les obligations fiscales
- Toute organisation qui doit conserver un historique des charges avec détails TVA