# PYOCH AI Connectors

PYOCH is designed with a multi-layered AI connector system that provides redundancy and fallback capabilities. The system follows this hierarchy:

## Connector Hierarchy

1. **Local Qwen Model** - Primary connector
2. **Local Mistral Model** - Secondary connector
3. **PYOCH's Own Brain** - Internal logic fallback
4. **OpenAI Cloud** - Backup connector (requires API key)

## Configuration

The AI connectors can be configured using environment variables:

```bash
# Qwen Local Model Endpoint
export QWEN_ENDPOINT="http://localhost:11434/api/generate"

# Mistral Local Model Endpoint
export MISTRAL_ENDPOINT="http://localhost:11434/api/generate"

# OpenAI Configuration
export OPENAI_API_KEY="your-openai-api-key"
export OPENAI_ENDPOINT="https://api.openai.com/v1/chat/completions"
```

## Setup Instructions

### 1. Local Models (Qwen and Mistral)

To use local models, you need to have Ollama running with both models:

```bash
# Install Ollama (if not already installed)
curl -fsSL https://ollama.ai/install.sh | sh

# Pull the required models
ollama pull qwen:latest
ollama pull mistral:latest

# Run Ollama server
ollama serve
```

### 2. OpenAI Backup (Optional)

If you want to use OpenAI as a backup, set your API key:

```bash
export OPENAI_API_KEY="your-api-key-here"
```

## How It Works

1. **Primary**: PYOCH first attempts to use the local Qwen model
2. **Secondary**: If Qwen is unavailable, it tries the local Mistral model
3. **Fallback**: If both local models fail, PYOCH uses its own internal logic
4. **Backup**: As a last resort, if the internal logic fails, it falls back to OpenAI

This architecture ensures that PYOCH can continue to function even if external services are unavailable, with multiple layers of redundancy.

## Troubleshooting

- If local models are not responding, ensure Ollama is running and the models are pulled
- Check that environment variables are properly set
- Monitor the logs to see which connector is being used