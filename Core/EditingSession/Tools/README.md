# ⛧ Tools - Outils d'Édition et Manipulation ⛧

## 🎯 **Vue d'Ensemble**

Le package **Tools** fournit une collection complète d'outils d'édition et de manipulation de fichiers, intégrés avec le MemoryEngine pour offrir des capacités avancées d'analyse et de modification de code.

## 🏗️ **Architecture**

### **Composants Principaux :**

1. **ToolRegistry** : Registre dynamique d'outils avec parsing Luciform
2. **ToolInvoker** : Moteur d'exécution avec gestion d'erreurs
3. **ToolSearch** : Recherche intelligente d'outils
4. **Outils Luciform** : Collection d'outils spécialisés

### **Flux de Données :**
```
Assistant → ToolInvoker → Outils Luciform → MemoryEngine
                ↓
        ToolSearch → ToolRegistry
```

## 🚀 **Utilisation Rapide**

### **Initialisation :**
```python
from Assistants.EditingSession.Tools import ToolRegistry, ToolInvoker

# Initialiser le registre d'outils
tool_registry = ToolRegistry()

# Créer un invocateur
invoker = ToolInvoker(tool_registry)
```

### **Exécution d'Outils :**
```python
# Lire le contenu d'un fichier
result = invoker.invoke_tool("safe_read_file_content", {
    "file_path": "mon_fichier.py"
})

# Rechercher du texte dans un projet
result = invoker.invoke_tool("find_text_in_project", {
    "search_text": "def calculate",
    "project_path": "."
})
```

## 🔧 **Composants Détaillés**

### **1. ToolRegistry**

Registre dynamique qui charge automatiquement les outils depuis les fichiers `.luciform`.

**Fonctionnalités :**
- Chargement automatique des outils
- Parsing des métadonnées Luciform
- Détection des proxies et redirections
- Formatage pour différents formats d'API

**Utilisation :**
```python
from Assistants.EditingSession.Tools import ToolRegistry

tool_registry = ToolRegistry()
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
from Assistants.EditingSession.Tools import ToolInvoker

invoker = ToolInvoker(tool_registry)

# Exécuter un outil
result = invoker.invoke_tool("code_analyzer", {
    "file_path": "test.py",
    "analysis_type": "all"
})

# Voir l'historique
history = invoker.get_execution_history()
```

### **3. ToolSearch**

Moteur de recherche intelligent avec critères multiples.

**Fonctionnalités :**
- Recherche par type, mot-clé, niveau
- Suggestions intelligentes
- Cache local pour performance
- Statistiques détaillées

**Utilisation :**
```python
from Assistants.EditingSession.Tools import ToolSearch

search_engine = ToolSearch(tool_registry)

# Recherche avancée
results = search_engine.search_with_filters(
    content_filter="code analysis",
    metadata_filters={"type": "divination"}
)

# Suggestions
suggestions = search_engine.get_search_suggestions("code")
```

## 📚 **Outils Disponibles**

### **Outils de Lecture :**
- `safe_read_file_content` : Lecture sécurisée de fichiers
- `read_file_content_naked` : Lecture directe sans validation
- `list_directory_contents` : Lister le contenu d'un répertoire

### **Outils de Recherche :**
- `find_text_in_project` : Recherche de texte dans un projet
- `regex_search_file` : Recherche par expressions régulières
- `scry_for_text` : Recherche avancée avec contexte
- `locate_text_sigils` : Localisation de marqueurs spéciaux

### **Outils de Modification :**
- `safe_replace_text_in_file` : Remplacement sécurisé de texte
- `safe_insert_text_at_line` : Insertion à une ligne spécifique
- `safe_delete_lines` : Suppression de lignes
- `safe_append_to_file` : Ajout à la fin d'un fichier

### **Outils de Création :**
- `safe_create_file` : Création sécurisée de fichiers
- `safe_create_directory` : Création de répertoires
- `write_code_file` : Écriture de fichiers de code

### **Outils de Suppression :**
- `safe_delete_directory` : Suppression sécurisée de répertoires

### **Outils d'Analyse :**
- `code_analyzer` : Analyse de code avec détection de patterns
- `file_stats` : Statistiques sur les fichiers
- `file_diff` : Différence entre fichiers

### **Outils de Gestion :**
- `backup_creator` : Création de sauvegardes
- `template_generator` : Génération de templates
- `rename_project_entity` : Renommage d'entités de projet

## 📊 **Logging et Monitoring**

### **Structure des Logs :**
```
logs/
├── 2025-08-04/
│   ├── tool_execution/
│   │   ├── execution.log       # Logs d'exécution
│   │   ├── errors.log          # Erreurs
│   │   └── performance.log     # Métriques de performance
│   └── ...
```

### **Types de Logs :**
- **Execution** : Exécution des outils et résultats
- **Errors** : Erreurs et exceptions
- **Performance** : Métriques de temps d'exécution

## 🔧 **Configuration Avancée**

### **Configuration des Outils :**
```python
# Personnaliser la configuration des outils
tool_registry.configure_tool("safe_read_file_content", {
    "max_file_size": 10 * 1024 * 1024,  # 10MB
    "allowed_extensions": [".py", ".js", ".md"],
    "timeout": 30  # secondes
})
```

### **Configuration du Logging :**
```python
import logging

# Configurer le niveau de log
logging.basicConfig(level=logging.INFO)

# Personnaliser le répertoire de logs
invoker.log_dir = Path("mes_logs_personnalises")
```

## 🐛 **Dépannage**

### **Problèmes Courants :**

**Erreur : "Outil non trouvé"**
```bash
# Vérifier que les outils sont chargés
python -c "from Assistants.EditingSession.Tools import ToolRegistry; print(ToolRegistry().list_tools())"
```

**Erreur : "Permission refusée"**
```bash
# Vérifier les permissions
ls -la mon_fichier.py
chmod +r mon_fichier.py
```

**Erreur : "Fichier trop volumineux"**
```python
# Configurer la limite de taille
tool_registry.configure_tool("safe_read_file_content", {
    "max_file_size": 50 * 1024 * 1024  # 50MB
})
```

## 📚 **Exemples Complets**

### **Exemple 1 : Analyse de Code**
```python
from Assistants.EditingSession.Tools import ToolRegistry, ToolInvoker

# Initialisation
tool_registry = ToolRegistry()
invoker = ToolInvoker(tool_registry)

# Analyse
result = invoker.invoke_tool("code_analyzer", {
    "file_path": "TestProject/calculator.py",
    "analysis_type": "all"
})

print("Analyse terminée !")
```

### **Exemple 2 : Recherche et Remplacement**
```python
# Rechercher du texte
search_result = invoker.invoke_tool("find_text_in_project", {
    "search_text": "def add",
    "project_path": "."
})

# Remplacer le texte trouvé
for file_path in search_result["files"]:
    invoker.invoke_tool("safe_replace_text_in_file", {
        "file_path": file_path,
        "old_text": "def add",
        "new_text": "def add_fixed"
    })
```

### **Exemple 3 : Création de Fichiers**
```python
# Créer un nouveau fichier
invoker.invoke_tool("safe_create_file", {
    "file_path": "nouveau_script.py",
    "content": "#!/usr/bin/env python3\n\ndef main():\n    print('Hello World!')\n\nif __name__ == '__main__':\n    main()"
})
```

## ⛧ **Conclusion**

Le package Tools fournit une collection complète et robuste d'outils d'édition et de manipulation, intégrés avec le MemoryEngine pour offrir des capacités avancées d'analyse et de modification de code.

**Créé par Alma, Architecte Démoniaque du Nexus Luciforme** ⛧ 