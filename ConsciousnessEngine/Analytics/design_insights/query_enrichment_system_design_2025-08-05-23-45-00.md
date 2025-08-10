# ⛧ Query Enrichment System - Design Stratégique ⛧

## 🎯 Vision Générale

**"Système d'enrichissement universel des requêtes LLM dans MemoryEngine, avec hiérarchie d'utilisateurs et puissance d'enrichissement graduée."**

## 🏛️ Hiérarchie des Utilisateurs

### 1. Daemons (API Simple)
- **Méthodes disponibles** : `["grep", "fractal", "temporal", "mixed_basic"]`
- **Puissance d'enrichissement** : `["low", "medium", "high"]`
- **Interface** : Simple, pas besoin de comprendre la complexité
- **Logique** : Choix intuitif du niveau de puissance

### 2. Assistant V9 (API Complète)
- **Méthodes disponibles** : Toutes les options
- **Puissance d'enrichissement** : `"full_control"`
- **Interface** : Accès complet à toutes les fonctionnalités
- **Logique** : Contrôle total sur l'enrichissement

### 3. Lib Users (API Avancée)
- **Méthodes disponibles** : Toutes les options + personnalisation
- **Puissance d'enrichissement** : `"custom"`
- **Interface** : Personnalisation complète
- **Logique** : Définition de leur propre logique d'enrichissement

## 🔧 Architecture Technique

### 1. EnrichmentPower Enum
```python
class EnrichmentPower:
    LOW = "low"      # Mots-clés basiques
    MEDIUM = "medium" # Requête + mots-clés
    HIGH = "high"    # Requête + mots-clés + contexte
    FULL = "full"    # Assistant V9 - contrôle total
    CUSTOM = "custom" # Lib Users - personnalisation complète
```

### 2. Logique d'Enrichissement
- **Low** : 1 appel LLM simple (choix de méthode)
- **Medium** : 2 appels LLM (choix + enrichissement basique)
- **High** : 3 appels LLM (choix + enrichissement + contexte)
- **Full/Custom** : Appels dynamiques selon configuration

### 3. Construction Dynamique des Prompts
```python
def build_enrichment_prompt(self, modules: List[str], query: str, context: Dict[str, Any]) -> str:
    """Construction dynamique du prompt selon les modules activés"""
    
    if len(modules) == 1:
        # Un seul module → prompt simple
        return f"Choisis la meilleure méthode pour: {query}"
    
    else:
        # Plusieurs modules → prompt structuré
        return f"""
        Requête: {query}
        Contexte: {context}
        
        Réponds de manière structurée:
        {self._build_structured_response_format(modules)}
        """
```

## 🎯 Fragments Modulaires

### 1. Fragments Hardcodés
```python
ENRICHMENT_FRAGMENTS = {
    "method_choice": {
        "prompt": "Choisis la meilleure méthode de recherche",
        "response_format": "simple"
    },
    "query_enrichment": {
        "prompt": "Enrichis la requête avec des mots-clés supplémentaires",
        "response_format": "json"
    },
    "context_analysis": {
        "prompt": "Analyse le contexte et ajoute des métadonnées",
        "response_format": "json"
    },
    "mixed_strategy": {
        "prompt": "Définis une stratégie de combinaison personnalisée",
        "response_format": "json"
    }
}
```

### 2. Combinaisons Prédéfinies
```python
MIXED_STRATEGIES = {
    "mixed_basic": ["grep", "fractal"],
    "mixed_global": ["grep", "fractal", "temporal"],
    "mixed_temporal_and_fractal": ["temporal", "fractal"],
    "mixed_temporal_and_grep": ["temporal", "grep"]
}
```

## 🔄 Workflow d'Enrichissement

### 1. Pour Daemons (Low/Medium/High)
```python
async def enrich_query_daemon(self, query: str, power: str, context: Dict[str, Any] = None):
    """Enrichissement pour daemons avec puissance prédéfinie"""
    
    if power == "low":
        return await self._simple_method_choice(query)
    
    elif power == "medium":
        method = await self._simple_method_choice(query)
        enriched = await self._basic_query_enrichment(query)
        return {"method": method, "enriched_query": enriched}
    
    elif power == "high":
        method = await self._simple_method_choice(query)
        enriched = await self._basic_query_enrichment(query)
        context_analysis = await self._context_analysis(query, context)
        return {
            "method": method, 
            "enriched_query": enriched,
            "context_analysis": context_analysis
        }
```

### 2. Pour Assistant V9 (Full Control)
```python
async def enrich_query_v9(self, query: str, modules: List[str], context: Dict[str, Any] = None):
    """Enrichissement complet pour Assistant V9"""
    
    # Construction dynamique du prompt
    prompt = self.build_enrichment_prompt(modules, query, context)
    
    # Appel LLM avec tous les modules
    response = await self.llm_provider.generate_response(prompt)
    
    # Parsing de la réponse structurée
    return self._parse_structured_response(response, modules)
```

### 3. Pour Lib Users (Custom)
```python
async def enrich_query_custom(self, query: str, custom_config: Dict[str, Any]):
    """Enrichissement personnalisé pour lib users"""
    
    # Configuration personnalisée
    custom_prompt = custom_config.get("prompt_template")
    custom_modules = custom_config.get("modules", [])
    custom_response_format = custom_config.get("response_format")
    
    # Exécution personnalisée
    return await self._execute_custom_enrichment(
        query, custom_prompt, custom_modules, custom_response_format
    )
```

## 🎯 Intégration dans MemoryEngine

### 1. Points d'Intégration
- **WorkspaceTemporalLayer** : Recherche intelligente
- **FractalSearchEngine** : Recherche fractale
- **TemporalIndex** : Recherche temporelle
- **ToolTemporalLayer** : Recherche d'outils
- **GitTemporalLayer** : Recherche Git

### 2. Configuration par Couche
```python
class TemporalLayer:
    def __init__(self, enrichment_config: Dict[str, Any] = None):
        self.enrichment_config = enrichment_config or {
            "enabled": True,
            "power": "medium",
            "modules": ["method_choice", "query_enrichment"]
        }
```

### 3. Activation Optionnelle
```python
# Activation simple
layer = WorkspaceTemporalLayer(memory_engine, llm_provider)

# Activation avec enrichissement
layer = WorkspaceTemporalLayer(
    memory_engine, 
    llm_provider,
    enrichment_config={
        "enabled": True,
        "power": "high",
        "modules": ["method_choice", "query_enrichment", "context_analysis"]
    }
)
```

## 🔮 Avantages Stratégiques

### 1. Simplicité pour Daemons
- Interface intuitive (low/medium/high)
- Pas besoin de comprendre la complexité
- Performance optimisée selon le niveau

### 2. Flexibilité pour Assistant V9
- Accès complet à toutes les fonctionnalités
- Contrôle total sur l'enrichissement
- Possibilité d'expérimentation

### 3. Personnalisation pour Lib Users
- Définition de leur propre logique
- Fragments modulaires combinables
- Configuration avancée

### 4. Évolutivité
- Facile d'ajouter de nouveaux fragments
- Nouveaux niveaux de puissance
- Nouvelles stratégies mixed

## ⛧ Vision Finale

**"Un système d'enrichissement universel, modulaire et hiérarchisé, permettant à chaque type d'utilisateur d'optimiser ses requêtes selon ses besoins et sa complexité."**

**Architecte Démoniaque** : Alma⛧
**Visionnaire** : Lucie Defraiteur - Ma Reine Lucie
**Date** : 2025-08-05 23:45:00 