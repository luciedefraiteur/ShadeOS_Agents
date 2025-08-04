#!/usr/bin/env python3
"""
⛧ Script de Détermination du Type de Requête ⛧
Script modulaire pour l'Archiviste Daemon
"""

import json
import subprocess
import time
from pathlib import Path
from typing import Dict, Any, Optional


def determine_query_type_with_ai(message: str, model: str = "qwen2.5:7b-instruct", timeout: int = 30) -> Dict[str, Any]:
    """
    Détermine le type de requête en utilisant l'IA.
    
    Args:
        message: Le message à analyser
        model: Le modèle Ollama à utiliser
        timeout: Timeout en secondes
    
    Returns:
        Dict avec query_type, confidence, reasoning, etc.
    """
    
    # Charger le prompt
    prompt_file = Path(__file__).parent.parent / "prompts" / "determine_query_type.luciform"
    
    try:
        with open(prompt_file, 'r', encoding='utf-8') as f:
            prompt = f.read()
    except FileNotFoundError:
        print(f"⚠️ Fichier prompt non trouvé: {prompt_file}")
        return _fallback_determination(message)
    
    # Construire le prompt complet
    full_prompt = f"""{prompt}

## 📨 **MESSAGE À ANALYSER**

{message}

## 📤 **RÉPONSE REQUISE**

Analyse le message ci-dessus et réponds avec le JSON approprié :"""

    print(f"🤖 Appel IA pour déterminer le type de requête")
    print(f"📝 Message: {message[:50]}...")
    
    try:
        # Appel à Ollama
        cmd = ["ollama", "run", model, full_prompt]
        start_time = time.time()
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        ai_time = time.time() - start_time
        
        print(f"⏱️ Temps d'appel IA: {ai_time:.2f}s")
        
        if result.returncode == 0:
            response_text = result.stdout.strip()
            print(f"📄 Réponse IA ({len(response_text)} caractères): {response_text[:100]}...")
            
            # Essayer d'extraire le JSON
            json_data = _extract_json_from_response(response_text)
            
            if json_data:
                # Validation du JSON
                if _validate_query_type_response(json_data):
                    print(f"✅ Type de requête déterminé: {json_data.get('query_type')} (confiance: {json_data.get('confidence')}%)")
                    return json_data
                else:
                    print(f"⚠️ JSON invalide, fallback")
            else:
                print(f"⚠️ JSON non trouvé dans la réponse")
        else:
            print(f"❌ Erreur Ollama: {result.stderr}")
            
    except subprocess.TimeoutExpired:
        print(f"❌ Timeout lors de l'appel IA ({timeout}s)")
    except Exception as e:
        print(f"❌ Erreur lors de l'appel IA: {e}")
    
    # Fallback si erreur
    return _fallback_determination(message)


def _extract_json_from_response(response_text: str) -> Optional[Dict[str, Any]]:
    """Extrait le JSON de la réponse IA."""
    
    # Chercher dans les blocs de code
    json_start = response_text.find('```json')
    if json_start != -1:
        json_end = response_text.find('```', json_start + 7)
        if json_end != -1:
            json_str = response_text[json_start + 7:json_end].strip()
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                pass
    
    # Chercher du JSON direct
    try:
        return json.loads(response_text.strip())
    except json.JSONDecodeError:
        pass
    
    # Chercher du JSON dans des accolades
    start_brace = response_text.find('{')
    end_brace = response_text.rfind('}')
    if start_brace != -1 and end_brace != -1:
        json_str = response_text[start_brace:end_brace + 1]
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            pass
    
    return None


def _validate_query_type_response(json_data: Dict[str, Any]) -> bool:
    """Valide la structure de la réponse."""
    
    required_fields = ["query_type", "confidence"]
    valid_query_types = [
        "describe_memory_types",
        "contextual_search", 
        "explore_workspace",
        "store_context",
        "explore_timeline",
        "general_query"
    ]
    
    # Vérifier les champs requis
    for field in required_fields:
        if field not in json_data:
            print(f"⚠️ Champ manquant: {field}")
            return False
    
    # Vérifier le type de requête
    query_type = json_data.get("query_type")
    if query_type not in valid_query_types:
        print(f"⚠️ Type de requête invalide: {query_type}")
        return False
    
    # Vérifier la confiance
    confidence = json_data.get("confidence", 0)
    if not isinstance(confidence, (int, float)) or confidence < 0 or confidence > 100:
        print(f"⚠️ Confiance invalide: {confidence}")
        return False
    
    return True


def _fallback_determination(message: str) -> Dict[str, Any]:
    """Détermination de fallback basée sur des mots-clés simples."""
    
    message_lower = message.lower()
    
    # Mots-clés pour chaque type
    keywords = {
        "describe_memory_types": ["décris", "explique", "types", "mémoire", "mémoires"],
        "contextual_search": ["cherche", "trouve", "recherche", "où", "localise"],
        "explore_workspace": ["explore", "workspace", "projet", "structure", "fichiers"],
        "store_context": ["stocke", "sauvegarde", "garde", "mémorise", "contexte"],
        "explore_timeline": ["timeline", "historique", "conversation", "discussion", "avant"],
        "general_query": ["bonjour", "salut", "comment", "ça va", "merci"]
    }
    
    # Compter les correspondances
    scores = {}
    for query_type, words in keywords.items():
        score = sum(1 for word in words if word in message_lower)
        if score > 0:
            scores[query_type] = score
    
    # Déterminer le meilleur match
    if scores:
        best_type = max(scores, key=scores.get)
        confidence = min(85, scores[best_type] * 20)  # Max 85% pour fallback
    else:
        best_type = "general_query"
        confidence = 50
    
    return {
        "query_type": best_type,
        "confidence": confidence,
        "reasoning": f"Fallback basé sur mots-clés: {list(scores.keys()) if scores else 'aucun'}",
        "keywords_detected": [word for word in keywords.get(best_type, []) if word in message_lower],
        "intention": "fallback_detection",
        "method": "fallback"
    }


if __name__ == "__main__":
    # Test du script
    test_messages = [
        "Décris-moi les types de mémoire disponibles",
        "Cherche 'daemon' dans la mémoire", 
        "Explore le workspace du projet",
        "Comment ça va ?"
    ]
    
    print("🧪 Test du script determine_query_type")
    print("=" * 50)
    
    for message in test_messages:
        print(f"\n📨 Message: {message}")
        result = determine_query_type_with_ai(message)
        print(f"🎯 Résultat: {result}")
        print("-" * 30) 