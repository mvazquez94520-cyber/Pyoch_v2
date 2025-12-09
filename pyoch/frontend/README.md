# PYOCH Frontend

## Pages disponibles

Ce répertoire contient deux interfaces frontend pour le générateur PYOCH :

### 1. Page simple (`index.html`)
- Interface minimale avec un espace de texte pour le prompt
- Bouton "Générer" pour envoyer la requête au backend
- Affichage de la réponse du serveur
- Design épuré et facile à utiliser

### 2. Page alternative (`simple.html`)
- Version alternative avec un design légèrement différent
- Même fonctionnalité de base : prompt → génération → affichage
- Style visuel différent pour répondre à différents besoins

## Utilisation

Les deux pages communiquent avec le backend PYOCH via l'API sur `http://localhost:3030/evaluate`.

Assurez-vous que le serveur backend est démarré avant d'utiliser les interfaces.