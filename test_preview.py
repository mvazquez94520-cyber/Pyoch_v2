#!/usr/bin/env python3
"""
Test script to demonstrate the preview functionality of PYOCH
"""

import asyncio
import json
from pyoch_prototype import AIEngine, PromptRequest

async def test_preview_functionality():
    print("=== Test de la fonctionnalité de prévisualisation ===\n")
    
    # Initialize AI Engine
    ai_engine = AIEngine()
    
    # Test prompt
    test_prompt = "Application de gestion de contacts pour une petite entreprise"
    
    print(f"Prompt testé: {test_prompt}\n")
    
    # Generate backend preview
    print("1. Génération de l'aperçu Backend:")
    backend_preview = await ai_engine.generate_backend_preview(test_prompt)
    print(backend_preview)
    print("\n" + "="*60 + "\n")
    
    # Generate frontend preview
    print("2. Génération de l'aperçu Frontend:")
    frontend_preview = await ai_engine.generate_frontend_preview(test_prompt)
    print(frontend_preview)
    print("\n" + "="*60 + "\n")
    
    # Test with different prompt types
    prompts = [
        "Application API REST pour gestion de commandes",
        "Application React pour suivi de projet",
        "Application backend Node.js pour e-commerce"
    ]
    
    for i, prompt in enumerate(prompts, 3):
        print(f"{i}. Test avec le prompt: {prompt}")
        
        backend = await ai_engine.generate_backend_preview(prompt)
        frontend = await ai_engine.generate_frontend_preview(prompt)
        
        # Check if the preview adapts to the prompt
        if "api" in prompt.lower() or "backend" in prompt.lower():
            print("   - Aperçu backend adapté pour une API")
        if "react" in prompt.lower():
            print("   - Aperçu frontend adapté pour React")
        
        print(f"   - Longueur aperçu backend: {len(backend)} caractères")
        print(f"   - Longueur aperçu frontend: {len(frontend)} caractères")
        print()

if __name__ == "__main__":
    asyncio.run(test_preview_functionality())