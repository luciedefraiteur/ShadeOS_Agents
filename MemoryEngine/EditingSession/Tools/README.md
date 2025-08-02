# ⛧ Tools Package - Intégration OpenAI Agents SDK ⛧

**Package pour la gestion des outils avec intégration MemoryEngine et OpenAI Agents SDK.**

Créé par Alma, Architecte Démoniaque du Nexus Luciforme.

---

## 🎯 **Vue d'ensemble**

Ce package fournit une intégration complète entre :
- **MemoryEngine** : Mémoire contextuelle et analyse de code
- **Alma_toolset** : Outils d'édition et manipulation de fichiers
- **OpenAI Agents SDK** : Intelligence conversationnelle et orchestration

### **🔮 Philosophie :**
*"L'IA converse, la mémoire se souvient, les outils agissent."*

---

## 🏗️ **Architecture**

### **Composants Principaux :**

1. **ToolRegistry** : Registre dynamique d'outils avec parsing Luciform
2. **ToolInvoker** : Moteur d'exécution avec gestion d'erreurs
3. **ToolSearchEngine** : Recherche intelligente d'outils
4. **OpenAIAgentTools** : Intégration complète avec OpenAI Agents SDK

### **Flux de Données :**
```
OpenAI Agent → OpenAIAgentTools → ToolInvoker → Alma_toolset
                    ↓
            ToolSearchEngine → ToolRegistry → MemoryEngine
```

---

## 🚀 **Utilisation Rapide**

### **Initialisation :**
```python
from MemoryEngine.core.engine import MemoryEngine
from MemoryEngine.EditingSession.Tools import create_openai_agent_tools

# Initialiser MemoryEngine
memory_engine = MemoryEngine()

# Créer l'intégration OpenAI
openai_tools = create_openai_agent_tools(memory_engine)
```

### **Configuration pour OpenAI :**
```python
# Récupérer la configuration des outils
tools_config = openai_tools.get_openai_tools_config()

# Utiliser avec OpenAI Agents SDK
from openai import OpenAI
client = OpenAI()

response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Analyse ce fichier"}],
    tools=tools_config,
    tool_choice="auto"
)
```

### **Gestion des Appels d'Outils :**
```python
# Traiter les appels d'outils
for tool_call in response.choices[0].message.tool_calls:
    result = openai_tools.handle_tool_call(tool_call)
    print(f"Résultat: {result}")
```

---

## 🔧 **Composants Détaillés**

### **1. ToolRegistry**

Registre dynamique qui charge automatiquement les outils depuis les fichiers `.luciform`.

**Fonctionnalités :**
- Chargement automatique depuis `Alma_toolset/` et `Tools/Library/`
- Parsing des métadonnées Luciform
- Détection des proxies et redirections
- Formatage pour OpenAI Agents SDK

**Utilisation :**
```python
from MemoryEngine.EditingSession.Tools import initialize_tool_registry

tool_registry = initialize_tool_registry(memory_engine)
print(f"Outils disponibles: {len(tool_registry.tools)}")

# Lister les outils
tools = tool_registry.list_tools(filter_type="divination")
for tool in tools:
    print(f"- {tool['id']}: {tool['intent']}")
```

### **2. ToolInvoker**

Moteur d'exécution avec gestion d'erreurs complète et logging.

**Fonctionnalités :**
- Exécution sécurisée des outils
- Gestion des erreurs et exceptions
- Logging automatique dans MemoryEngine
- Support des appels OpenAI Agents SDK

**Utilisation :**
```python
from MemoryEngine.EditingSession.Tools import ToolInvoker

invoker = ToolInvoker(tool_registry)

# Exécution directe
result = invoker.invoke_tool("safe_replace_text_in_file", 
                           file_path="test.py", 
                           old_text="old", 
                           new_text="new")

# Exécution depuis OpenAI
result = invoker.invoke_tool_for_openai("safe_replace_text_in_file", 
                                       '{"file_path": "test.py", "old_text": "old", "new_text": "new"}')
```

### **3. ToolSearchEngine**

Moteur de recherche intelligent avec scoring et suggestions.

**Fonctionnalités :**
- Recherche par mot-clé avec scoring
- Filtrage par type, niveau, source
- Suggestions automatiques
- Historique des recherches

**Utilisation :**
```python
from MemoryEngine.EditingSession.Tools import ToolSearchEngine

search_engine = ToolSearchEngine(tool_registry)

# Recherche par mot-clé
results = search_engine.search_by_keyword("file", limit=5)
for result in results:
    print(f"- {result['tool_id']} (score: {result['score']})")

# Recherche avancée
results = search_engine.advanced_search({
    "type": "divination",
    "level": "avancé",
    "keyword": "regex"
})
```

### **4. OpenAIAgentTools**

Intégration complète avec OpenAI Agents SDK.

**Fonctionnalités :**
- Configuration automatique des outils
- Gestion des appels d'outils
- Contexte enrichi pour agents
- Suggestions d'outils intelligentes
- Workflows prédéfinis

**Utilisation :**
```python
from MemoryEngine.EditingSession.Tools import OpenAIAgentTools

openai_tools = OpenAIAgentTools(tool_registry)

# Contexte pour agent
context = openai_tools.get_context_for_agent("analyser un fichier Python", "my_file.py")

# Suggestions d'outils
suggestions = openai_tools.suggest_tools_for_task("modifier un fichier")

# Workflow exemple
workflow = openai_tools.create_workflow_example("file_editing")
```

---

## 📊 **Métriques et Monitoring**

### **Statistiques d'Exécution :**
```python
# Statistiques des outils
stats = openai_tools.get_agent_statistics()
print(f"Exécutions totales: {stats['tool_executions']['total_executions']}")
print(f"Outils disponibles: {stats['total_tools_available']}")
print(f"Outils les plus utilisés: {stats['most_used_tools']}")
```

### **Historique des Recherches :**
```python
# Historique des recherches
history = search_engine.get_search_history(limit=10)
for search in history:
    print(f"Recherche '{search['query']}': {search['total_results']} résultats")
```

---

## 🔄 **Workflows Prédéfinis**

### **1. Édition de Fichier :**
1. Analyse de la structure
2. Modification du contenu
3. Vérification du résultat

### **2. Analyse de Code :**
1. Lecture du contenu
2. Analyse de la structure
3. Recherche de patterns

### **3. Gestion de Projet :**
1. Exploration de la structure
2. Analyse des fichiers
3. Organisation du projet

---

## 🧪 **Tests**

Exécuter les tests d'intégration :
```bash
python test_openai_memoryengine_integration.py
```

Les tests vérifient :
- Initialisation du registre d'outils
- Recherche et suggestion d'outils
- Exécution d'outils
- Intégration OpenAI
- Workflows complets

---

## 🔮 **Évolutions Futures**

### **Fonctionnalités Prévues :**
- **Apprentissage automatique** : Amélioration des suggestions basée sur l'usage
- **Workflows personnalisés** : Création de workflows spécifiques
- **Intégration multi-agents** : Collaboration entre plusieurs agents
- **Métriques avancées** : Analyse de performance et optimisation

### **Optimisations :**
- **Cache intelligent** : Mise en cache des résultats fréquents
- **Exécution parallèle** : Exécution simultanée d'outils compatibles
- **Validation avancée** : Vérification préventive des paramètres

---

## 📚 **Documentation Technique**

### **Structure des Fichiers :**
```
MemoryEngine/EditingSession/Tools/
├── __init__.py              # Package principal
├── tool_registry.py         # Registre d'outils
├── tool_invoker.py          # Moteur d'exécution
├── tool_search.py           # Moteur de recherche
├── openai_integration.py    # Intégration OpenAI
└── README.md               # Documentation
```

### **Dépendances :**
- `MemoryEngine` : Mémoire contextuelle
- `Alma_toolset` : Outils d'édition
- `openai` : SDK OpenAI (optionnel)

---

**⛧ Intégration parfaite entre IA conversationnelle et mémoire mystique ! ⛧**

*"L'IA converse, la mémoire se souvient, les outils agissent - trinité de l'édition intelligente."* 