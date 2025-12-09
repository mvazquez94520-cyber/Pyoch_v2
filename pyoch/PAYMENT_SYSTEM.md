# Système de Paiement et Espace Client - PYOCH

## Description Générale

Ce système permet aux utilisateurs de :
- S'inscrire et se connecter à une plateforme sécurisée
- Générer des prévisualisations d'applications métiers
- Payer via PayPal pour obtenir l'application Windows complète
- Accéder à un espace client pour gérer leurs informations et téléchargements

## Architecture du Système

### 1. Authentification et Sécurité

- **JWT (JSON Web Tokens)** pour l'authentification
- **Hashage de mot de passe** avec bcrypt
- **Protection des routes** avec middleware d'authentification
- **Respect de la RGPD** avec gestion des données utilisateur

### 2. Paiement via PayPal

- Intégration avec l'API PayPal pour les paiements sécurisés
- Processus de paiement en deux étapes (création et exécution)
- Gestion des statuts de paiement (pending, completed, failed, refunded)

### 3. Génération d'Applications Windows

- Génération automatique d'exécutables Windows (.exe)
- Conservation des fichiers de téléchargement pendant 30 jours
- Système de nettoyage automatique des fichiers expirés

## Endpoints API

### Authentification
- `POST /register` - Création d'un nouvel utilisateur
- `POST /login` - Connexion d'un utilisateur existant

### Ressources protégées (nécessite un token JWT)
- `GET /profile` - Informations du profil utilisateur
- `GET /payments` - Historique des paiements
- `GET /applications` - Applications générées par l'utilisateur

### Paiement
- `POST /create-payment` - Création d'un paiement PayPal
- `POST /execute-payment` - Exécution d'un paiement PayPal après approbation

### Téléchargement
- `GET /download/{filename}` - Téléchargement d'une application générée

## Base de Données

### Tables
1. **users** - Informations des utilisateurs
2. **applications** - Applications générées par les utilisateurs
3. **payments** - Historique des transactions PayPal
4. **application_downloads** - Informations de téléchargement

## Sécurité

- Tous les mots de passe sont hashés avec bcrypt
- Les tokens JWT ont une durée de vie limitée (7 jours)
- Les routes sensibles sont protégées par authentification
- Les fichiers téléchargements expirent après 30 jours
- Respect des bonnes pratiques de sécurité web

## RGPD

- Droit à l'information : Les utilisateurs peuvent accéder à leurs données
- Conservation limitée : Les fichiers sont supprimés après 30 jours
- Les données personnelles sont stockées de manière sécurisée
- Aucune vente ou partage de données personnelles

## Processus de Paiement

1. L'utilisateur génère une prévisualisation d'application
2. S'il souhaite l'application complète, il initie un paiement
3. Le système crée un paiement PayPal et redirige l'utilisateur
4. Après paiement réussi, l'application Windows est générée automatiquement
5. L'utilisateur reçoit un lien de téléchargement valide 30 jours

## Installation et Configuration

### Variables d'environnement
Créer un fichier `.env` avec :
```
DATABASE_URL=postgresql://user:password@localhost/pyoch
JWT_SECRET=votre_cle_secrete_jwt
PAYPAL_CLIENT_ID=votre_client_id_paypal
PAYPAL_CLIENT_SECRET=votre_client_secret_paypal
```

### Migration de la base de données
```bash
# Créer la base de données
createdb pyoch

# Appliquer les migrations
# (Utilisez sqlx-cli ou votre outil de migration préféré)
```

### Lancement du serveur
```bash
cd backend
cargo run
```

## Frontend

Le frontend existant a été étendu pour inclure :
- Interface d'inscription et de connexion
- Espace client avec historique des paiements
- Gestion des téléchargements
- Intégration avec PayPal pour les paiements

## Génération d'Applications Windows

Le système de génération d'application Windows est configurable et peut être étendu pour :
- Générer des applications avec différentes fonctionnalités
- Créer des interfaces utilisateur personnalisées
- Intégrer des fonctionnalités spécifiques selon le type d'application (CRM, facturation, etc.)