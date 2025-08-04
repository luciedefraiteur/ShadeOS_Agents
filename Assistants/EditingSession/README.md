# 🧠 EditingSession - Système de Gestion des Sessions d'Édition ⛧

## Vue d'ensemble

Le module `EditingSession` fournit un système complet pour la gestion des sessions d'édition avec partitionnement intelligent des fichiers et localisation précise des modifications. Il est conçu pour fonctionner en harmonie avec le MemoryEngine et offre des capacités avancées d'analyse et de tracking des changements.

## 🏗️ Architecture

### Structure du Module
```
Assistants/EditingSession/
├── __init__.py                 # Module principal
├── README.md                   # Documentation
├── partitioning/               # Système de partitionnement
│   ├── __init__.py            # Interface principale
│   ├── partition_schemas.py   # Schémas de données
│   ├── location_tracker.py    # Tracking de localisation
│   ├── error_logger.py        # Logging d'erreurs
│   ├── language_registry.py   # Registre des langages
│   ├── ast_partitioners/      # Partitionneurs AST
│   │   ├── __init__.py
│   │   ├── base_ast_partitioner.py
│   │   ├── python_ast_partitioner.py
│   │   └── tree_sitter_partitioner.py
│   └── fallback_strategies/   # Stratégies de fallback
│       ├── __init__.py
│       ├── regex_partitioner.py
│       ├── textual_partitioner.py
│       └── emergency_partitioner.py
├── Tools/                     # Outils d'édition et manipulation
│   ├── __init__.py
│   ├── tool_registry.py       # Registre d'outils
│   ├── tool_invoker.py        # Moteur d'exécution
│   ├── tool_search.py         # Recherche d'outils
│   └── [outils luciform]      # Outils d'édition
└── development_waves/          # Évolutions futures
```

## 🎯 Fonctionnalités Principales

### 1. **Partitionnement Intelligent**
- **Analyse AST** : Partitionnement basé sur l'arbre syntaxique
- **Support Multi-langages** : Python, JavaScript, TypeScript, etc.
- **Stratégies de Fallback** : Regex, textuel, d'urgence
- **Localisation Précise** : Tracking des positions exactes

### 2. **Outils d'Édition**
- **Registre d'Outils** : Gestion dynamique des outils Luciform
- **Moteur d'Exécution** : Exécution sécurisée des outils
- **Recherche Intelligente** : Recherche d'outils par critères
- **Intégration MemoryEngine** : Stockage et récupération de contexte

### 3. **Registre des Langages**
- **Détection Automatique** : Identification du langage par extension/contenu
- **Configuration Flexible** : Support de nouveaux langages
- **Partitionneurs Spécialisés** : Optimisés par langage

### 4. **Tracking de Localisation**
- **Positions Exactes** : Ligne, colonne, offset
- **Historique des Modifications** : Suivi des changements
- **Validation de Cohérence** : Vérification des positions

### 5. **Logging d'Erreurs**
- **Logging Structuré** : Erreurs détaillées avec contexte
- **Gestion Globale** : Logger centralisé
- **Récupération d'Erreurs** : Stratégies de fallback automatiques

## 🚀 Utilisation

### Import Basique
```python
from Assistants.EditingSession import partition_file, detect_language

# Partitionner un fichier
result = partition_file("mon_fichier.py")

# Détecter le langage
lang = detect_language("mon_fichier.py")
```

### Utilisation des Outils
```python
from Assistants.EditingSession.Tools import ToolRegistry, ToolInvoker

# Initialiser le registre d'outils
tool_registry = ToolRegistry()

# Créer un invocateur
invoker = ToolInvoker(tool_registry)

# Exécuter un outil
result = invoker.invoke_tool("safe_read_file_content", {
    "file_path": "mon_fichier.py"
})
```

### Utilisation Avancée
```python
from Assistants.EditingSession import (
    LanguageRegistry,
    global_language_registry,
    PartitionResult,
    global_error_logger
)

# Utiliser le registre global
registry = global_language_registry

# Partitionner avec options
result = registry.partition_file(
    "mon_fichier.py",
    method="ast",
    include_comments=True,
    include_whitespace=False
)

# Vérifier les erreurs
if global_error_logger.has_errors():
    errors = global_error_logger.get_errors()
    print(f"Erreurs détectées : {len(errors)}")
```

## 📊 Schémas de Données

### PartitionResult
```python
@dataclass
class PartitionResult:
    success: bool
    file_path: str
    language: str
    method: PartitionMethod
    blocks: List[PartitionBlock]
    metadata: Dict[str, Any]
    errors: List[str]
    warnings: List[str]
```

### PartitionBlock
```python
@dataclass
class PartitionBlock:
    block_type: BlockType
    content: str
    location: PartitionLocation
    metadata: Dict[str, Any]
    children: List['PartitionBlock']
```

### PartitionLocation
```python
@dataclass
class PartitionLocation:
    start_line: int
    start_column: int
    end_line: int
    end_column: int
    start_offset: int
    end_offset: int
```

## 🔧 Partitionneurs Disponibles

### 1. **AST Partitionneurs**
- **BaseASTPartitioner** : Classe de base pour les partitionneurs AST
- **PythonASTPartitioner** : Spécialisé pour Python
- **TreeSitterPartitioner** : Support multi-langages via Tree-sitter

### 2. **Stratégies de Fallback**
- **RegexPartitioner** : Partitionnement par expressions régulières
- **TextualPartitioner** : Partitionnement basé sur le texte
- **EmergencyPartitioner** : Partitionnement d'urgence minimal

## 🎨 Types de Blocs

### BlockType Enum
```python
class BlockType(Enum):
    # Code
    FUNCTION = "function"
    CLASS = "class"
    METHOD = "method"
    VARIABLE = "variable"
    IMPORT = "import"
    
    # Documentation
    COMMENT = "comment"
    DOCSTRING = "docstring"
    
    # Structure
    MODULE = "module"
    BLOCK = "block"
    STATEMENT = "statement"
    
    # Spécial
    UNKNOWN = "unknown"
    ERROR = "error"
```

## ⚙️ Configuration

### Variables d'Environnement
```bash
# Activer le logging détaillé
export EDITING_SESSION_DEBUG=1

# Configurer le niveau de log
export EDITING_SESSION_LOG_LEVEL=INFO

# Désactiver Tree-sitter
export EDITING_SESSION_NO_TREE_SITTER=1
```

### Configuration Programmatique
```python
from Assistants.EditingSession import global_error_logger

# Configurer le logging
global_error_logger.set_level("DEBUG")
global_error_logger.enable_file_logging("editing_session.log")

# Configurer les options de partitionnement
registry = global_language_registry
registry.set_default_options({
    "include_comments": True,
    "include_whitespace": False,
    "max_block_size": 1000
})
```

## 🔍 Détection des Langages

### Langages Supportés
- **Python** : `.py`, `.pyw`, `.pyx`
- **JavaScript** : `.js`, `.jsx`
- **TypeScript** : `.ts`, `.tsx`
- **Java** : `.java`
- **C/C++** : `.c`, `.cpp`, `.h`, `.hpp`
- **Go** : `.go`
- **Rust** : `.rs`
- **PHP** : `.php`
- **Ruby** : `.rb`
- **Shell** : `.sh`, `.bash`, `.zsh`

### Détection Automatique
```python
from Assistants.EditingSession import detect_language

# Par extension
lang = detect_language("script.py")  # "python"

# Par contenu (analyse du shebang, etc.)
lang = detect_language("script", content="#!/usr/bin/env python3")
```

## 🚨 Gestion d'Erreurs

### Types d'Erreurs
- **PartitioningError** : Erreur générale de partitionnement
- **LocationTrackingError** : Erreur de tracking de localisation
- **PartitionValidationError** : Erreur de validation

### Logging d'Erreurs
```python
from Assistants.EditingSession import (
    global_error_logger,
    log_partitioning_error,
    log_partitioning_warning
)

# Logger une erreur
log_partitioning_error(
    "Erreur de parsing",
    file_path="script.py",
    line=10,
    details="Syntaxe invalide"
)

# Vérifier les erreurs
if global_error_logger.has_errors():
    for error in global_error_logger.get_errors():
        print(f"Erreur: {error.message}")
```

## 🔄 Stratégies de Fallback

### Ordre de Priorité
1. **AST Partitionner** : Partitionnement syntaxique précis
2. **Regex Partitionner** : Partitionnement par patterns
3. **Textual Partitionner** : Partitionnement basé sur le texte
4. **Emergency Partitionner** : Partitionnement minimal

### Configuration des Fallbacks
```python
from Assistants.EditingSession import LanguageRegistry

registry = LanguageRegistry()

# Configurer les fallbacks pour Python
registry.configure_fallbacks("python", [
    "ast",
    "regex",
    "textual",
    "emergency"
])
```

## 📈 Métriques et Performance

### Métriques Disponibles
- **Temps de partitionnement** : Performance par méthode
- **Taux de succès** : Pourcentage de partitionnements réussis
- **Taille des blocs** : Distribution des tailles
- **Erreurs par langage** : Statistiques d'erreurs

### Optimisation
```python
from Assistants.EditingSession import global_language_registry

# Activer le cache
global_language_registry.enable_caching()

# Configurer les limites
global_language_registry.set_limits({
    "max_file_size": 10 * 1024 * 1024,  # 10MB
    "max_block_count": 10000,
    "timeout": 30  # secondes
})
```

## 🔮 Évolutions Futures

### Développement en Vagues
- **Vague 1** : Partitionnement de base et AST
- **Vague 2** : Stratégies de fallback avancées
- **Vague 3** : Intégration avec MemoryEngine
- **Vague 4** : Analyse sémantique et IA

### Fonctionnalités Prévues
- **Analyse Sémantique** : Compréhension du code
- **IA Integration** : Suggestions intelligentes
- **Collaboration** : Sessions multi-utilisateurs
- **Versioning** : Historique des modifications

## 🤝 Intégration avec MemoryEngine

### Utilisation Conjointe
```python
from MemoryEngine import memory_engine
from Assistants.EditingSession import partition_file

# Partitionner un fichier
result = partition_file("script.py")

# Stocker dans MemoryEngine
for block in result.blocks:
    memory_engine.store(
        content=block.content,
        metadata={
            "type": block.block_type.value,
            "location": block.location,
            "file": result.file_path
        },
        strata="cognitive"
    )
```

### Extensions Futures
- **ToolMemoryExtension** : Indexation des outils d'édition
- **ToolSearchExtension** : Recherche dans les sessions
- **SessionManager** : Gestion des sessions actives

---

*Module créé par : Alma, Architecte Démoniaque du Nexus Luciforme*  
*Version : 2.0.0*  
*Intégré dans : Assistants*  
*Refactorisé : 2025-08-04* 