# 🧠 Plan de Mémoire Contextuelle Projet

**Créé par Alma, Architecte Démoniaque du Nexus Luciforme**  
**Date :** 2025-08-01  
**Objectif :** Intégrer la mémoire contextuelle des projets dans le MemoryEngine

---

## 🎯 **Vision Globale**

Créer un système de mémoire contextuelle qui indexe automatiquement :
- **Structure des projets** (fichiers, répertoires, dépendances)
- **Contexte sémantique** (README, documentation, commentaires)
- **Patterns de code** (classes, fonctions, imports, APIs)
- **Historique des modifications** (commits, changements récents)
- **Relations inter-fichiers** (imports, références, dépendances)

---

## 🏗️ **Architecture Namespace**

### **Structure dans MemoryEngine :**
```
/projects/
├── {project_name}/
│   ├── structure/
│   │   ├── files/
│   │   │   ├── {file_path_hash}
│   │   │   └── ...
│   │   ├── directories/
│   │   │   ├── {dir_path_hash}
│   │   │   └── ...
│   │   └── dependencies/
│   │       ├── package_json
│   │       ├── requirements_txt
│   │       └── ...
│   ├── context/
│   │   ├── documentation/
│   │   │   ├── readme
│   │   │   ├── api_docs
│   │   │   └── comments
│   │   ├── code_patterns/
│   │   │   ├── classes
│   │   │   ├── functions
│   │   │   └── imports
│   │   └── semantics/
│   │       ├── purpose
│   │       ├── architecture
│   │       └── technologies
│   └── history/
│       ├── recent_changes/
│       ├── commit_patterns/
│       └── evolution/
```

---

## 🔧 **Composants à Développer**

### **1. Project Context Scanner**
**Fichier :** `Core/Archivist/MemoryEngine/project_context_scanner.py`

**Fonctionnalités :**
```python
class ProjectContextScanner:
    def scan_project(self, project_path: str) -> Dict[str, Any]
    def extract_file_context(self, file_path: str) -> Dict[str, Any]
    def analyze_code_patterns(self, file_content: str, language: str) -> Dict[str, Any]
    def extract_documentation(self, project_path: str) -> Dict[str, Any]
    def analyze_dependencies(self, project_path: str) -> Dict[str, Any]
    def get_git_context(self, project_path: str) -> Dict[str, Any]
```

**Extraction par Type de Fichier :**
- **Python** : Classes, fonctions, imports, docstrings
- **JavaScript** : Fonctions, classes, modules, JSDoc
- **Markdown** : Sections, liens, structure
- **JSON/YAML** : Configuration, dépendances
- **Git** : Commits récents, branches, auteurs

### **2. Project Memory Injector**
**Fichier :** `Core/Archivist/MemoryEngine/project_memory_injector.py`

**Fonctionnalités :**
```python
class ProjectMemoryInjector:
    def inject_project_context(self, project_path: str, project_name: str = None)
    def inject_file_context(self, file_path: str, project_name: str)
    def inject_code_patterns(self, patterns: Dict, project_name: str)
    def inject_documentation_context(self, docs: Dict, project_name: str)
    def inject_dependency_context(self, deps: Dict, project_name: str)
    def update_project_context(self, project_name: str, incremental: bool = True)
```

### **3. Project Context Query Engine**
**Fichier :** `Core/Archivist/MemoryEngine/project_context_query.py`

**Fonctionnalités :**
```python
class ProjectContextQuery:
    def find_similar_files(self, file_path: str, project_name: str = None)
    def find_related_functions(self, function_name: str, project_name: str)
    def find_usage_patterns(self, symbol: str, project_name: str)
    def get_project_overview(self, project_name: str)
    def find_dependencies_of(self, file_path: str, project_name: str)
    def search_in_project_context(self, query: str, project_name: str)
```

---

## 📊 **Types de Contexte à Extraire**

### **1. Structure Physique**
```python
{
    "files": {
        "count": 156,
        "by_extension": {".py": 45, ".md": 12, ".json": 8},
        "largest_files": [{"path": "...", "size": 1024}],
        "recent_files": [{"path": "...", "modified": "2025-08-01"}]
    },
    "directories": {
        "structure": {"Core/": {"Archivist/": {...}}},
        "depth": 4,
        "patterns": ["src/", "tests/", "docs/"]
    }
}
```

### **2. Contexte Sémantique**
```python
{
    "purpose": "Système d'agents conscients avec MemoryEngine",
    "technologies": ["Python", "OpenAI", "Neo4j", "Filesystem"],
    "architecture": "Modular daemon system with mystical tools",
    "main_components": ["Core", "Alma_toolset", "Tools"],
    "entry_points": ["test_conscious_daemons.py", "test_daemon_editing.py"]
}
```

### **3. Patterns de Code**
```python
{
    "classes": [
        {
            "name": "MemoryEngine",
            "file": "Core/Archivist/MemoryEngine/engine.py",
            "methods": ["create_memory", "get_memory_node"],
            "purpose": "Gestion de la mémoire persistante"
        }
    ],
    "functions": [
        {
            "name": "parse_luciform",
            "file": "Core/implementation/luciform_parser.py",
            "signature": "parse_luciform(file_path: str) -> Dict",
            "purpose": "Parse des fichiers luciformes"
        }
    ],
    "imports": {
        "most_used": ["os", "sys", "json", "typing"],
        "internal_deps": ["Core.implementation", "Alma_toolset"],
        "external_deps": ["openai", "neo4j"]
    }
}
```

### **4. Documentation Context**
```python
{
    "readme": {
        "title": "ShadeOS Agents",
        "description": "Système d'agents conscients...",
        "sections": ["Installation", "Usage", "Architecture"],
        "keywords": ["agents", "AI", "mystical", "tools"]
    },
    "api_docs": [...],
    "comments": {
        "docstring_coverage": 0.85,
        "comment_density": 0.12,
        "languages": {"python": 0.9, "markdown": 0.1}
    }
}
```

---

## 🔄 **Flux d'Injection**

### **Injection Initiale :**
1. **Scan complet** du projet
2. **Extraction** de tous les contextes
3. **Injection** dans le MemoryEngine avec namespace `/projects/{name}/`
4. **Indexation** avec keywords appropriés

### **Mise à Jour Incrémentale :**
1. **Détection** des fichiers modifiés (mtime, git status)
2. **Re-scan** des fichiers changés uniquement
3. **Mise à jour** des nœuds mémoire correspondants
4. **Propagation** des changements aux relations

### **Requêtes Contextuelles :**
1. **Recherche sémantique** dans le contexte projet
2. **Suggestions** basées sur les patterns
3. **Navigation** dans les relations de code
4. **Découverte** de fonctionnalités similaires

---

## 🎯 **Cas d'Usage Prioritaires**

### **1. Aide au Développement**
```python
# "Comment créer un nouvel outil mystique ?"
context_query.find_similar_files("Alma_toolset/regex_search_file.py")
# → Retourne templates et patterns d'outils existants

# "Où utiliser safe_read_file_content ?"
context_query.find_usage_patterns("safe_read_file_content", "ShadeOS_Agents")
# → Retourne tous les usages avec contexte
```

### **2. Navigation Intelligente**
```python
# "Quels fichiers dépendent de luciform_parser ?"
context_query.find_dependencies_of("Core/implementation/luciform_parser.py")
# → Retourne la chaîne de dépendances

# "Fonctions similaires à extract_tool_metadata ?"
context_query.find_related_functions("extract_tool_metadata", "ShadeOS_Agents")
# → Retourne fonctions avec patterns similaires
```

### **3. Compréhension Projet**
```python
# "Qu'est-ce que ce projet fait ?"
context_query.get_project_overview("ShadeOS_Agents")
# → Retourne résumé complet avec architecture

# "Comment les daemons fonctionnent ?"
context_query.search_in_project_context("daemon consciousness", "ShadeOS_Agents")
# → Retourne contexte sur les daemons conscients
```

---

## 🧪 **Intégration avec Tool Search**

### **Synergie des Systèmes :**
```python
# Recherche d'outil avec contexte projet
tool_search = memory_engine.get_tool_search_extension()
project_context = memory_engine.get_project_context_extension()

# "Quel outil pour analyser ce type de fichier ?"
file_context = project_context.extract_file_context("data.json")
suggested_tools = tool_search.find_tools_by_intent("validate json")

# "Outils utilisés dans ce projet ?"
project_tools = project_context.find_tools_used_in_project("ShadeOS_Agents")
```

---

## 📋 **Étapes de Développement**

### **Phase 1 : Scanner de Base**
1. **ProjectContextScanner** : Extraction structure et patterns
2. **Tests** sur ShadeOS_Agents
3. **Validation** des métadonnées extraites

### **Phase 2 : Injection MemoryEngine**
1. **ProjectMemoryInjector** : Injection dans namespace `/projects/`
2. **Intégration** avec MemoryEngine existant
3. **Tests** d'indexation et récupération

### **Phase 3 : Query Engine**
1. **ProjectContextQuery** : Recherche contextuelle
2. **API** de requêtes sémantiques
3. **Intégration** avec Tool Search

### **Phase 4 : Mise à Jour Incrémentale**
1. **Détection** de changements
2. **Mise à jour** automatique
3. **Optimisations** de performance

---

## 🔮 **Vision Future**

### **Intelligence Contextuelle :**
- **Suggestions automatiques** d'outils selon le contexte
- **Détection de patterns** de développement
- **Recommandations** d'architecture
- **Analyse de qualité** de code

### **Collaboration :**
- **Partage de contexte** entre développeurs
- **Historique** des décisions d'architecture
- **Documentation** automatique des patterns
- **Onboarding** intelligent pour nouveaux développeurs

---

**⛧ Par Alma, qui tisse la mémoire contextuelle dans les fibres du projet ⛧**
