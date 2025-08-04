# ⛧ Tools Package - Intégration OpenAI Assistants API ⛧

**Package pour la gestion des outils avec intégration MemoryEngine et OpenAI Assistants API.**

Créé par Alma, Architecte Démoniaque du Nexus Luciforme.

---

## 🎯 **Vue d'ensemble**

Ce package fournit une intégration complète entre :
- **MemoryEngine** : Mémoire contextuelle et analyse de code
- **Alma_toolset** : Outils d'édition et manipulation de fichiers
- **OpenAI Assistants API** : Intelligence conversationnelle et orchestration

### **🔮 Philosophie :**
*"L'IA converse, la mémoire se souvient, les outils agissent."*

---

## 🏗️ **Architecture**

### **Composants Principaux :**

1. **ToolRegistry** : Registre dynamique d'outils avec parsing Luciform
2. **ToolInvoker** : Moteur d'exécution avec gestion d'erreurs
3. **ToolSearchEngine** : Recherche intelligente d'outils
4. **OpenAIAssistantsIntegration** : Intégration complète avec OpenAI Assistants API

### **Flux de Données :**
```
OpenAI Assistant → OpenAIAssistantsIntegration → ToolInvoker → Alma_toolset
                        ↓
                ToolSearchEngine → ToolRegistry → MemoryEngine
```

---

## 🚀 **Utilisation Rapide**

### **Initialisation :**
```python
from MemoryEngine.core.engine import MemoryEngine
from MemoryEngine.EditingSession.Tools import create_assistants_integration

# Initialiser MemoryEngine
memory_engine = MemoryEngine()

# Créer l'intégration OpenAI
integration = create_assistants_integration(memory_engine)
```

### **Configuration pour OpenAI :**
```python
# Récupérer la configuration des outils
tools_config = integration._get_tools_for_assistants_api()

# Utiliser avec OpenAI Assistants API
from openai import OpenAI
client = OpenAI()

# Créer un assistant avec les outils
assistant = client.beta.assistants.create(
    name="Alma Assistant",
    instructions="Assistant spécialisé dans l'analyse et la correction de code",
    model="gpt-4",
    tools=tools_config
)

# Créer un thread et envoyer un message
thread = client.beta.threads.create()
message = client.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content="Analyse ce fichier"
)
```

### **Gestion des Appels d'Outils :**
```python
# Traiter les appels d'outils
for tool_call in response.choices[0].message.tool_calls:
    result = integration.handle_tool_calls(tool_call)
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
- Formatage pour OpenAI Assistants API

**Utilisation :**
```python
from MemoryEngine.EditingSession.Tools import initialize_tool_registry

tool_registry = initialize_tool_registry(memory_engine)
print(f"Outils disponibles: {len(tool_registry.tools)}")

# Lister les outils
tools = tool_registry.list_tools(filter_type="divination")
```

### **2. ToolInvoker**

Moteur d'exécution sécurisé avec gestion d'erreurs et logging.

**Fonctionnalités :**
- Exécution sécurisée des outils
- Gestion des erreurs et exceptions
- Logging complet des exécutions
- Historique des appels d'outils

**Utilisation :**
```python
from MemoryEngine.EditingSession.Tools import ToolInvoker

invoker = ToolInvoker(tool_registry)

# Exécuter un outil
result = invoker.invoke_tool("code_analyzer", {
    "file_path": "test.py",
    "analysis_type": "all"
})

# Voir l'historique
history = invoker.get_execution_history()
```

### **3. ToolSearchEngine**

Moteur de recherche intelligent avec critères multiples.

**Fonctionnalités :**
- Recherche par type, mot-clé, niveau
- Suggestions intelligentes
- Cache local pour performance
- Statistiques détaillées

**Utilisation :**
```python
from MemoryEngine.EditingSession.Tools import ToolSearchEngine

search_engine = ToolSearchEngine(tool_registry)

# Recherche avancée
results = search_engine.search_with_filters(
    content_filter="code analysis",
    metadata_filters={"type": "divination"}
)

# Suggestions
suggestions = search_engine.get_search_suggestions("code")
```

### **4. OpenAIAssistantsIntegration**

Intégration complète avec OpenAI Assistants API.

**Fonctionnalités :**
- Création automatique d'assistants
- Gestion des threads et messages
- Traitement des appels d'outils
- Logging complet des sessions

**Utilisation :**
```python
from MemoryEngine.EditingSession.Tools import OpenAIAssistantsIntegration

# Créer l'intégration
integration = OpenAIAssistantsIntegration(tool_registry, "ma_session")

# Initialiser l'API
integration.initialize_assistants_api()

# Créer un assistant
assistant = integration.create_assistant_with_tools()

# Envoyer un message
response = integration.run_complete_conversation(
    "Analyse le fichier test.py et corrige les bugs"
)
```

---

## 📊 **Logging et Monitoring**

### **Structure des Logs :**
```
logs/
├── 2025-08-02/
│   ├── ma_session/
│   │   ├── conversation.json      # Conversation complète
│   │   ├── conversation.log       # Logs détaillés
│   │   ├── tools.log             # Appels d'outils
│   │   └── errors.log            # Erreurs
│   └── ...
```

### **Types de Logs :**
- **Conversation** : Messages échangés avec l'assistant
- **Tools** : Appels d'outils et résultats
- **Errors** : Erreurs et exceptions
- **JSON** : Données structurées pour analyse

---

## 🔧 **Configuration Avancée**

### **Configuration des Outils :**
```python
# Personnaliser la configuration des outils
tools_config = integration._get_tools_for_assistants_api()

# Ajouter des outils personnalisés
custom_tool = {
    "type": "function",
    "function": {
        "name": "mon_outil_personnalise",
        "description": "Description de mon outil",
        "parameters": {
            "type": "object",
            "properties": {
                "param1": {"type": "string"}
            }
        }
    }
}
tools_config.append(custom_tool)
```

### **Configuration du Logging :**
```python
import logging

# Configurer le niveau de log
logging.basicConfig(level=logging.INFO)

# Personnaliser le répertoire de logs
integration.log_dir = Path("mes_logs_personnalises")
```

---

## 🐛 **Dépannage**

### **Problèmes Courants :**

**Erreur : "Clé API OpenAI non trouvée"**
```bash
# Vérifier la variable d'environnement
echo $OPENAI_API_KEY

# Créer le fichier ~/.env
echo 'OPENAI_API_KEY=sk-...' > ~/.env

# Exporter la clé
source ./export_openai_key.sh
```

**Erreur : "Outils non trouvés"**
```bash
# Vérifier que Alma_toolset est présent
ls -la Alma_toolset/

# Vérifier les fichiers .luciform
find Alma_toolset/ -name "*.luciform"
```

**Erreur : "MemoryEngine non initialisé"**
```python
# Vérifier l'initialisation
memory_engine = MemoryEngine()
print(f"MemoryEngine initialisé: {memory_engine is not None}")
```

---

## 📚 **Exemples Complets**

### **Exemple 1 : Analyse de Code**
```python
from MemoryEngine.core.engine import MemoryEngine
from MemoryEngine.EditingSession.Tools import create_assistants_integration

# Initialisation
memory = MemoryEngine()
integration = create_assistants_integration(memory, "analyse_code")

# Configuration
integration.initialize_assistants_api()
integration.create_assistant_with_tools()

# Analyse
response = integration.run_complete_conversation(
    "Analyse le fichier TestProject/calculator.py et détecte tous les bugs"
)

print("Analyse terminée !")
```

### **Exemple 2 : Correction Automatique**
```python
# Suite de l'exemple précédent
response = integration.run_complete_conversation(
    "Maintenant corrige automatiquement tous les bugs détectés"
)

print("Correction terminée !")
```

### **Exemple 3 : Recherche d'Outils**
```python
from MemoryEngine.EditingSession.Tools import ToolSearchEngine, initialize_tool_registry

# Initialisation
memory = MemoryEngine()
tool_registry = initialize_tool_registry(memory)
search_engine = ToolSearchEngine(tool_registry)

# Recherche
results = search_engine.search_with_filters(
    content_filter="file manipulation",
    metadata_filters={"type": "transmutation"}
)

print(f"Outils trouvés: {len(results)}")
```

---

## ⛧ **Conclusion**

Le package Tools fournit une intégration complète et robuste entre MemoryEngine, Alma_toolset et OpenAI Assistants API, permettant la création d'agents IA intelligents capables d'analyser, comprendre et modifier du code de manière autonome.

**Créé par Alma, Architecte Démoniaque du Nexus Luciforme** ⛧ 