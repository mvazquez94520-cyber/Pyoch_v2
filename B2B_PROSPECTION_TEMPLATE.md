# Template PYOCH - Application de Prospection B2B GPU

## Description
Ce template permet de générer une application de prospection B2B spécialisée dans l'identification d'entreprises en France pouvant avoir besoin de workstations équipées de GPU. L'application permet de rechercher des entreprises selon des critères spécifiques et d'exporter les résultats vers un fichier Excel.

## Fonctionnalités

### 1. Recherche d'entreprises
- Saisie de mots-clés pour la recherche d'entreprises
- Utilisation de SERP API (implémenté via placeholder pour démonstration)
- Critères de recherche :
  - Secteurs d'activité : IA/ML, rendu 3D, simulation scientifique, cryptomonnaie, design industriel, VFX
  - Taille d'entreprise : PME et grandes entreprises (10+ employés)
  - Localisation : France

### 2. Export vers Excel
- Export des résultats de recherche vers un fichier Excel
- Format : Nom de l'entreprise, Email, Secteur, Nombre d'employés, Localisation, Technologie, Statut de contact
- Structure du fichier Excel :
  - Colonne A : Nom de l'entreprise
  - Colonne B : Email
  - Colonne C : Secteur
  - Colonne D : Nombre d'employés
  - Colonne E : Localisation
  - Colonne F : Technologie
  - Colonne G : Statut de contact

### 3. Interface utilisateur
- Interface web avec sélection de type d'application
- Section spécifique pour la prospection B2B
- Champ de saisie pour les mots-clés
- Boutons pour recherche et export
- Affichage des résultats en format JSON

## Architecture

### Backend (Rust)
- Module `prospection_b2b` : Contient les structures de données et la logique métier
- Routes API :
  - `POST /prospection/search` : Recherche d'entreprises par mots-clés
  - `GET /prospection/export` : Export des données vers Excel
- Structure `Company` : Modèle de données pour les entreprises
- Méthode `export_to_excel` : Génération de fichiers Excel avec xlsxwriter

### Frontend (HTML/JavaScript)
- Interface utilisateur avec sélecteur de type d'application
- Section spécifique pour la prospection B2B
- Gestion dynamique des sections (affichage/masquage selon le type sélectionné)
- Fonctions JavaScript pour la recherche et l'export

## API Endpoints

### Recherche d'entreprises
- **URL** : `/prospection/search`
- **Méthode** : POST
- **Content-Type** : application/json
- **Requête** :
  ```json
  {
    "keywords": ["intelligence artificielle", "gpu"]
  }
  ```
- **Réponse** :
  ```json
  {
    "companies": [...],
    "total_found": 3,
    "search_time": 2
  }
  ```

### Export vers Excel
- **URL** : `/prospection/export`
- **Méthode** : GET
- **Réponse** :
  ```json
  {
    "status": "export completed",
    "filename": "prospects.xlsx",
    "companies_exported": 3
  }
  ```

## Exemple de données
L'application génère des exemples d'entreprises pour la démonstration :
- TechAI Solutions (contact@techai-solutions.fr) - IA/ML
- Render3D Studio (info@render3d-studio.fr) - Rendu 3D
- VFX Pro (hello@vfxpro.fr) - Effets Visuels

## Utilisation
1. Sélectionner "Prospection B2B GPU" dans le sélecteur de type d'application
2. Saisir des mots-clés dans le champ dédié (ex: "intelligence artificielle, GPU, machine learning")
3. Cliquer sur "Rechercher les entreprises"
4. Une fois les résultats obtenus, cliquer sur "Exporter vers Excel"
5. Le fichier Excel sera généré avec les données des entreprises

## Extension future
- Intégration avec SERP API réel (SERPAPI) pour la recherche d'entreprises
- Ajout de filtres avancés (localisation, taille d'entreprise, technologie spécifique)
- Génération automatique d'emails personnalisés
- Suivi des campagnes de prospection
- Intégration avec des outils CRM existants

## Technologies utilisées
- Rust (backend)
- Actix-web (framework web)
- xlsxwriter (génération Excel)
- HTML/CSS/JavaScript (frontend)
- JSON (format d'échange)