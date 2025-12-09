# Intégration du Template B2B Prospection dans PYOCH

## Résumé

Ce document explique comment le template de prospection B2B GPU a été intégré dans l'écosystème PYOCH comme un nouveau type d'application métier.

## Modifications apportées

### 1. Backend (Rust)

#### Fichiers créés :
- `/backend/src/templates/prospection_b2b/mod.rs` : Module principal avec structures de données et logique métier
- `/backend/src/templates.rs` : Gestion des routes spécifiques au template

#### Fichiers modifiés :
- `/backend/src/main.rs` : 
  - Ajout de l'import du module templates
  - Ajout de la configuration des routes pour le template
  - Extension de la liste des types d'applications avec "prospection_b2b"

- `/backend/Cargo.toml` : 
  - Ajout des dépendances xlsxwriter pour la génération de fichiers Excel

#### Fonctionnalités ajoutées :
- Nouvelles routes API : `/prospection/search` et `/prospection/export`
- Structure `Company` pour représenter les entreprises prospectées
- Méthode `export_to_excel` pour générer des fichiers Excel
- Moteur de prospection B2B avec recherche simulée via SERP API

### 2. Frontend (HTML/JavaScript)

#### Fichier modifié :
- `/frontend/static/index.html` :
  - Ajout d'une section spécifique pour la prospection B2B
  - Champ de saisie pour les mots-clés
  - Boutons pour la recherche et l'export Excel
  - Gestion dynamique de l'affichage selon le type d'application sélectionné
  - Fonctions JavaScript pour appeler les nouvelles routes API

## Fonctionnement

### Sélection du template
1. L'utilisateur sélectionne "Prospection B2B GPU" dans le sélecteur de type d'application
2. L'interface bascule vers la section spécifique avec les champs de recherche

### Flux d'utilisation
1. Saisie des mots-clés dans le champ dédié
2. Clic sur "Rechercher les entreprises" → appel à `/prospection/search`
3. Affichage des résultats (simulés pour la démonstration)
4. Clic sur "Exporter vers Excel" → appel à `/prospection/export`
5. Génération du fichier Excel avec les données des entreprises

## Structure des données

### Company
```rust
pub struct Company {
    pub id: Uuid,
    pub name: String,           // Nom de l'entreprise
    pub email: String,          // Email de contact
    pub sector: String,         // Secteur d'activité
    pub employees: u32,         // Nombre d'employés
    pub location: String,       // Localisation
    pub technology: Option<String>, // Technologies utilisées
    pub contact_status: ContactStatus, // Statut du contact
    pub created_at: chrono::DateTime<chrono::Utc>,
    pub updated_at: chrono::DateTime<chrono::Utc>,
}
```

### Format Excel exporté
- Colonne A : Nom de l'entreprise
- Colonne B : Email
- Colonne C : Secteur
- Colonne D : Nombre d'employés
- Colonne E : Localisation
- Colonne F : Technologie
- Colonne G : Statut de contact

## Extension future

### Intégration SERP API
Le template est conçu pour intégrer facilement SERP API pour la recherche d'entreprises réelles :
- Remplacer la fonction de recherche simulée par des appels réels à SERP API
- Ajouter des paramètres de recherche avancés (localisation, taille d'entreprise, etc.)

### Fonctionnalités supplémentaires
- Système de scoring des prospects
- Génération d'emails personnalisés
- Suivi des interactions
- Intégration avec des outils CRM

## Conformité RGPD

Le template respecte les principes RGPD :
- Les données sont traitées localement
- Les utilisateurs contrôlent les données exportées
- Les emails sont générés de manière personnalisée mais responsable