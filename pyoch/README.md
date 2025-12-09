# PYOCH - Plateforme de Génération d'Applications Métiers

PYOCH est une plateforme conçue pour générer des applications métiers complexes (CRM, facturation, gestion de projets, etc.) en interagant avec l'utilisateur via des prompts. La plateforme utilise des moteurs d'IA locaux (Mistral et QWEN) pour générer du code et des applications, et peut également se connecter à une API OpenAI pour des fonctionnalités cloud.

## Fonctionnalités

- Génération d'applications métiers basées sur des templates
- Moteur de règles linéaires pour gérer la logique métier
- Intégration avec des modèles d'IA locaux (QWEN, Mistral)
- Système de feedback pour l'auto-apprentissage
- Interface web intuitive

## Prérequis

- Rust (1.70 ou supérieur)
- Ollama installé et exécutant les modèles Qwen et Mistral
- PostgreSQL (optionnel pour la persistence)

## Installation

1. Clonez le dépôt:
```bash
git clone <repository-url>
cd pyoch
```

2. Installez les dépendances:
```bash
cargo build
```

3. Configurez vos variables d'environnement:
```bash
cp .env.example .env
# Modifiez le fichier .env selon vos besoins
```

4. Lancez le serveur:
```bash
cargo run
```

Le serveur sera disponible à l'adresse `http://localhost:3030`

## Configuration d'Ollama

Pour utiliser les modèles locaux, assurez-vous qu'Ollama est installé et en cours d'exécution:

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

## Structure du Projet

```
pyoch/
├── src/
│   ├── main.rs           # Point d'entrée principal
│   ├── models.rs         # Structures de données
│   ├── ai_engine.rs      # Connecteurs IA (Qwen, Mistral, OpenAI)
│   └── rule_engine.rs    # Moteur de règles et logique métier
├── static/               # Fichiers statiques (HTML, CSS, JS)
├── Cargo.toml            # Dépendances Rust
└── .env                  # Variables d'environnement
```

## Utilisation

1. Accédez à l'interface web à `http://localhost:3030`
2. Sélectionnez un type d'application métier
3. Décrivez votre besoin dans le champ de texte
4. Cliquez sur "Envoyer" pour générer l'application
5. Évaluez la pertinence des résultats et fournissez un feedback

## Sécurité et Confidentialité

- Toutes les données restent sur votre serveur local
- Les modèles d'IA fonctionnent localement
- Les communications avec les services cloud sont optionnelles et chiffrées

## Contribution

Les contributions sont les bienvenues! N'hésitez pas à soumettre des issues et des pull requests.