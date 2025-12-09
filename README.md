# PYOCH - Plateforme de Génération d'Applications Métiers

PYOCH est une plateforme conçue pour générer des applications métiers complexes (CRM, facturation, gestion de projets, etc.) en interagant avec l'utilisateur via des prompts. La plateforme utilise des moteurs d'IA locaux (Mistral et QWEN) pour générer du code et des applications, et peut également se connecter à une API OpenAI pour des fonctionnalités cloud.

## Architecture du Projet

Le projet est structuré de la manière suivante :

```
/workspace/
├── pyoch/                    # Version Rust de PYOCH (complète)
│   ├── src/
│   │   ├── main.rs          # Point d'entrée principal
│   │   ├── models.rs        # Structures de données
│   │   ├── ai_engine.rs     # Connecteurs IA (Qwen, Mistral, OpenAI)
│   │   └── rule_engine.rs   # Moteur de règles et logique métier
│   ├── static/              # Fichiers statiques (HTML, CSS, JS)
│   ├── Cargo.toml           # Dépendances Rust
│   └── README.md            # Documentation spécifique à la version Rust
├── pyoch_prototype.py       # Version Python du prototype
├── requirements.txt         # Dépendances Python
└── README.md               # Ce fichier
```

## Fonctionnalités

- Génération d'applications métiers basées sur des templates
- Moteur de règles linéaires pour gérer la logique métier
- Intégration avec des modèles d'IA locaux (QWEN, Mistral)
- Système de feedback pour l'auto-apprentissage
- Interface web intuitive

## Versions Disponibles

### 1. Version Rust (complète)

La version complète de PYOCH est implémentée en Rust avec les fonctionnalités suivantes :

- Serveur web avec Actix-web
- Moteur de règles avancé
- Intégration avec Ollama pour les modèles Qwen et Mistral
- Système de feedback pour l'amélioration continue
- Interface web complète

### 2. Version Python (prototype)

Un prototype fonctionnel est également disponible en Python pour démonstration :

- API REST avec FastAPI
- Moteur de règles simulé
- Interface web intégrée
- Système de feedback basique

## Installation et Démarrage

### Version Rust

1. Assurez-vous d'avoir Rust installé :
```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source $HOME/.cargo/env
```

2. Allez dans le répertoire pyoch et lancez le projet :
```bash
cd /workspace/pyoch
cargo run
```

3. Le serveur sera disponible à l'adresse `http://localhost:3030`

### Version Python (prototype)

1. Installez les dépendances :
```bash
pip install -r requirements.txt
```

2. Lancez le prototype :
```bash
python pyoch_prototype.py
```

3. Le serveur sera disponible à l'adresse `http://localhost:8000`

## Configuration d'Ollama

Pour utiliser les modèles locaux, assurez-vous qu'Ollama est installé et en cours d'exécution :

```bash
# Téléchargez les modèles requis
ollama pull qwen:latest
ollama pull mistral:latest

# Lancez Ollama
ollama serve
```

## API Endpoints

- `GET /health` - Vérifie l'état de santé de l'application
- `POST /evaluate` - Évalue un prompt métier et génère une réponse
- `POST /feedback` - Soumet un feedback sur une règle générée
- `GET /app-types` - Récupère les types d'applications disponibles
- `GET /` - Interface web principale

## Utilisation

1. Accédez à l'interface web
2. Sélectionnez un type d'application métier
3. Décrivez votre besoin dans le champ de texte
4. Cliquez sur "Envoyer" pour générer l'application
5. Évaluez la pertinence des résultats et fournissez un feedback

## Auto-apprentissage

Le système collecte les feedbacks utilisateurs et ajuste les règles en conséquence pour s'améliorer continuellement.

## Sécurité et Confidentialité

- Toutes les données restent sur votre serveur local
- Les modèles d'IA fonctionnent localement
- Les communications avec les services cloud sont optionnelles et chiffrées

## Déploiement

La plateforme est conçue pour fonctionner en local mais peut être déployée sur un serveur AWS avec les configurations appropriées.

## Contribution

Les contributions sont les bienvenues! N'hésitez pas à soumettre des issues et des pull requests.
