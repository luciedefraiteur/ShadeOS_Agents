# 🤖 Core/LLMProviders - Système de Providers LLM

**Date :** 2025-08-07  
**Auteur :** Alma (via Lucie Defraiteur)  
**Contexte :** Système abstrait de providers LLM pour ShadeOS_Agents

---

## 🎯 Vue d'Ensemble

Le module `Core/LLMProviders` fournit un système abstrait et réutilisable de providers LLM pour tous les composants de ShadeOS_Agents. Il inclut validation, gestion d'erreurs, estimation de taille et configuration flexible.

---

## 🏗️ Architecture

### **✅ Composants Principaux :**

#### **1. Provider Abstrait**
```python
from Core.LLMProviders import (
    # Interface principale
    LLMProvider,
    ProviderStatus,
    LLMResponse,
    ValidationResult,
    ProviderType,
    ErrorType
)
```

#### **2. Providers Concrets**
```python
from Core.LLMProviders import (
    # Providers disponibles
    OpenAIProvider,
    LocalProvider,
    LocalProviderHTTP,
    
    # Factory pattern
    ProviderFactory
)
```

#### **3. Factory Pattern**
```python
from Core.LLMProviders import ProviderFactory

# Création de provider
provider = ProviderFactory.create_provider("openai", api_key="...")

# Validation de provider
validation = await ProviderFactory.validate_provider(provider)
```

---

## 📁 Structure

### **✅ Core/LLMProviders/**
```
Core/LLMProviders/
├── __init__.py              # Interface principale
├── llm_provider.py          # Classe abstraite LLMProvider
├── provider_factory.py      # Factory pattern
├── openai_provider.py       # Provider OpenAI
├── local_provider.py        # Provider Ollama (subprocess)
├── local_provider_http.py   # Provider Ollama (HTTP)
└── README.md               # Documentation
```

---

## 🔧 Fonctionnalités

### **✅ Providers Supportés :**

#### **1. OpenAI Provider**
- **Modèles** : GPT-4, GPT-3.5-turbo, etc.
- **Capacités** : Chat completion, text generation, streaming, function calling
- **Configuration** : API key, model, organization, timeout, max_tokens
- **Avantages** : Haute qualité, fonction calling, streaming

#### **2. Local Provider (HTTP)**
- **Modèles** : Ollama models (qwen2.5:7b, llama3.1:8b, etc.)
- **Capacités** : Text generation, chat completion, local inference
- **Configuration** : Model, ollama_host, timeout, temperature
- **Avantages** : Local, privé, rapide, pas de coût

#### **3. Local Provider (Subprocess)**
- **Modèles** : Ollama models via subprocess
- **Capacités** : Text generation, chat completion, local inference
- **Configuration** : Model, ollama_binary, timeout, temperature
- **Avantages** : Compatibilité legacy, contrôle direct

### **✅ Fonctionnalités Avancées :**

#### **1. Validation Automatique**
```python
# Validation complète d'un provider
validation = await ProviderFactory.validate_provider(provider)

if validation.valid:
    print(f"Provider {validation.provider_type} validé en {validation.test_time:.2f}s")
else:
    print(f"Erreur: {validation.error}")
```

#### **2. Estimation de Taille**
```python
# Estimation des tokens
estimated_tokens = provider.estimate_tokens(prompt)

# Validation de la taille
is_valid = provider.validate_request_size(prompt, max_tokens=4000)
```

#### **3. Gestion d'Erreurs**
```python
# Types d'erreurs supportés
from Core.LLMProviders import ErrorType

error_types = [
    ErrorType.CONNECTION_ERROR,
    ErrorType.AUTHENTICATION_ERROR,
    ErrorType.RATE_LIMIT_ERROR,
    ErrorType.QUOTA_EXCEEDED,
    ErrorType.INVALID_REQUEST,
    ErrorType.UNKNOWN_ERROR
]
```

---

## 🚀 Utilisation

### **1. Création de Provider :**
```python
from Core.LLMProviders import ProviderFactory

# Provider OpenAI
openai_provider = ProviderFactory.create_provider(
    "openai",
    api_key="sk-...",
    model="gpt-4",
    timeout=30
)

# Provider Local
local_provider = ProviderFactory.create_provider(
    "local",
    model="qwen2.5:7b",
    ollama_host="http://localhost:11434",
    temperature=0.7
)
```

### **2. Validation de Provider :**
```python
# Validation complète
provider, validation = await ProviderFactory.create_and_validate_provider(
    "openai",
    api_key="sk-..."
)

if validation.valid:
    print(f"Provider {validation.provider_type} prêt")
    print(f"Capacités: {validation.capabilities}")
else:
    print(f"Erreur de validation: {validation.error}")
```

### **3. Utilisation du Provider :**
```python
# Appel simple
response = await provider.generate_text(
    prompt="Explique-moi l'intelligence artificielle",
    max_tokens=500
)

# Appel avec streaming
async for chunk in provider.stream_generate_text(
    prompt="Écris une histoire",
    max_tokens=1000
):
    print(chunk, end="", flush=True)
```

### **4. Gestion d'Erreurs :**
```python
try:
    response = await provider.generate_text(prompt)
except Exception as e:
    if provider.last_error_type == ErrorType.RATE_LIMIT_ERROR:
        # Attendre et réessayer
        await asyncio.sleep(60)
        response = await provider.generate_text(prompt)
    elif provider.last_error_type == ErrorType.QUOTA_EXCEEDED:
        # Basculer vers provider local
        local_provider = ProviderFactory.create_provider("local")
        response = await local_provider.generate_text(prompt)
```

---

## 📊 Métriques

### **✅ Performance :**
- **OpenAI** : Latence 1-3s, haute qualité
- **Local HTTP** : Latence 0.5-2s, qualité variable
- **Local Subprocess** : Latence 0.3-1.5s, contrôle direct

### **✅ Fiabilité :**
- **Validation** : 100% des providers validés avant utilisation
- **Fallback** : Basculement automatique en cas d'erreur
- **Retry** : Logique de retry intelligente
- **Monitoring** : Métriques de performance en temps réel

### **✅ Coût :**
- **OpenAI** : Pay-per-token (0.01-0.03$/1K tokens)
- **Local** : Gratuit, coût hardware uniquement
- **Hybride** : Optimisation automatique des coûts

---

## 🔄 Intégration

### **✅ Avec TemporalFractalMemoryEngine :**
```python
from Core.LLMProviders import ProviderFactory
from TemporalFractalMemoryEngine import TemporalEngine

# Provider avec mémoire temporelle
temporal_engine = TemporalEngine()
provider = ProviderFactory.create_provider("openai")

# Enregistrement des appels dans la mémoire
temporal_node = await temporal_engine.create_temporal_node(
    content=f"LLM Call: {prompt[:100]}...",
    metadata={
        "provider": provider.provider_type,
        "model": provider.model,
        "tokens_used": response.usage.total_tokens
    }
)
```

### **✅ Avec Core/Agents :**
```python
from Core.Agents.V10 import V10Assistant
from Core.LLMProviders import ProviderFactory

# Assistant avec provider configuré
provider = ProviderFactory.create_provider("openai")
assistant = V10Assistant(llm_provider=provider)

# Exécution avec provider optimisé
result = await assistant.execute_task("Analyse ce code")
```

---

## 📝 Développement

### **✅ Ajout d'un Nouveau Provider :**
1. **Créer le provider** : `nouveau_provider.py`
2. **Implémenter l'interface** : Hériter de `LLMProvider`
3. **Ajouter à la factory** : Dans `provider_factory.py`
4. **Ajouter les tests** : `tests/test_nouveau_provider.py`
5. **Documenter** : Dans le README

### **✅ Standards de Code :**
- **Type hints** : Obligatoires
- **Docstrings** : Documentation complète
- **Tests** : Couverture > 90%
- **Validation** : Validation des entrées
- **Error handling** : Gestion robuste d'erreurs

---

## 🔗 Liens

### **📋 Documentation :**
- [Provider Interface](./llm_provider.py)
- [Factory Pattern](./provider_factory.py)
- [Testing Guide](./tests/README.md)

### **📋 Code :**
- [OpenAI Provider](./openai_provider.py)
- [Local Provider](./local_provider.py)
- [Local HTTP Provider](./local_provider_http.py)

---

**Rapport généré automatiquement par Alma**  
**Date :** 2025-08-07  
**Statut :** Documentation complète du système de providers LLM
