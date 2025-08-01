# 🔍 Plan du Système de Recherche d'Outils Mystiques

**Créé par Alma, Architecte Démoniaque du Nexus Luciforme**  
**Date :** 2025-08-01  
**Objectif :** Intégrer la recherche d'outils dans le MemoryEngine avec indexation automatique

---

## 🎯 **Vision Globale**

Créer un système de recherche d'outils mystiques intégré au MemoryEngine existant, permettant de :
- **Indexer automatiquement** tous les outils depuis leurs luciformes
- **Rechercher par critères mystiques** (type, mots-clés, niveau, intention)
- **Maintenir une séparation claire** entre outils et autres mémoires
- **Fournir une API unifiée** pour la découverte d'outils

---

## 🏗️ **Architecture du Système**

### **Namespace dans MemoryEngine :**
```
/tools/
├── divination/
│   ├── regex_search_file
│   └── find_text_in_project
├── protection/
│   └── backup_creator
├── transmutation/
│   └── template_generator
├── scrying/
│   └── file_diff
├── augury/
│   └── file_stats
├── memory/
│   ├── remember
│   ├── recall
│   └── forget
├── inscription/
│   ├── safe_create_file
│   └── safe_overwrite_file
├── revelation/
│   └── safe_read_file_content
└── metamorphosis/
    └── safe_replace_text_in_file
```

### **Flux de Données :**
1. **Luciformes** → **Parser** → **Métadonnées**
2. **Métadonnées** → **MemoryEngine** → **Nœuds /tools/**
3. **Requêtes** → **Recherche MemoryEngine** → **Résultats filtrés**

---

## 📋 **Étapes de Développement**

### **Étape 1 : Parser de Métadonnées Luciformes** 🔧
**Fichier :** `Core/implementation/luciform_tool_metadata_parser.py`

**Objectif :** Extraire les métadonnées mystiques depuis les fichiers .luciform

**Fonctionnalités :**
- `extract_tool_metadata(luciform_path)` → Dict métadonnées
- `scan_luciform_directories()` → Liste de tous les outils
- Support des types mystiques harmonisés
- Extraction : type, intent, level, keywords, signature, symbolic_layer, usage_context

**Métadonnées Extraites :**
```python
{
    'tool_id': 'regex_search_file',
    'type': 'divination',
    'intent': 'Révéler les patterns cachés...',
    'level': 'avancé',
    'keywords': ['regex', 'pattern', 'search', 'context'],
    'signature': 'regex_search_file(file_path: str, pattern: str, ...)',
    'symbolic_layer': '⛧ Révélateur des patterns cachés...',
    'usage_context': 'Quand un agent doit analyser...',
    'file_path': '/path/to/luciform'
}
```

**Dépendances :**
- `Core.implementation.luciform_parser` (existant)
- Parcours récursif des répertoires de luciformes

---

### **Étape 2 : Extension MemoryEngine pour Outils** 🧠
**Fichier :** `Core/Archivist/MemoryEngine/tool_search_extension.py`

**Objectif :** Ajouter des capacités de recherche d'outils au MemoryEngine

**Fonctionnalités Principales :**
```python
class ToolSearchExtension:
    def __init__(self, memory_engine)
    
    # Indexation
    def index_all_tools(force_reindex=False)
    def register_tool(tool_metadata)
    def inject_tool_from_luciform(luciform_path)
    
    # Recherche
    def find_tools_by_type(tool_type: str) → List[Dict]
    def find_tools_by_keyword(keyword: str) → List[Dict]
    def find_tools_by_level(level: str) → List[Dict]
    def find_tools_by_intent(intent_query: str) → List[Dict]
    def search_tools(**criteria) → List[Dict]
    
    # Utilitaires
    def get_tool_info(tool_id: str) → Dict
    def list_all_tool_types() → List[str]
    def get_tools_by_namespace() → Dict[str, List]
```

**Intégration MemoryEngine :**
- Utilise `memory_engine.create_memory()` pour indexer
- Namespace `/tools/` pour séparer des autres mémoires
- Strate `cognitive` pour les outils
- Keywords automatiques : [type, tool_id, ...keywords_luciform]

---

### **Étape 3 : Fonctions d'Injection et Enregistrement** 📝
**Objectifs :** Automatiser l'ajout d'outils au système

#### **3.1 register_tool(tool_metadata)**
```python
def register_tool(self, tool_metadata: Dict[str, Any]):
    """
    Enregistre un outil dans le MemoryEngine.
    
    Args:
        tool_metadata: Métadonnées complètes de l'outil
    """
    tool_id = tool_metadata['tool_id']
    tool_type = tool_metadata.get('type', 'unknown')
    
    # Chemin dans le namespace
    tool_path = f"/tools/{tool_type}/{tool_id}"
    
    # Création du nœud mémoire
    self.memory_engine.create_memory(
        path=tool_path,
        content=json.dumps(tool_metadata, indent=2),
        summary=f"{tool_type.title()}: {tool_metadata.get('intent', tool_id)}",
        keywords=[tool_type, tool_id] + tool_metadata.get('keywords', []),
        strata="cognitive"
    )
```

#### **3.2 inject_tool_from_luciform(luciform_path)**
```python
def inject_tool_from_luciform(self, luciform_path: str):
    """
    Injecte un outil depuis son fichier luciform.
    
    Args:
        luciform_path: Chemin vers le fichier .luciform
    """
    # Parse des métadonnées
    metadata = self.parser.extract_tool_metadata(luciform_path)
    if metadata and metadata.get('tool_id'):
        # Enregistrement dans le MemoryEngine
        self.register_tool(metadata)
        return True
    return False
```

#### **3.3 Auto-indexation au Démarrage**
```python
def index_all_tools(self, force_reindex: bool = False):
    """
    Indexe automatiquement tous les outils trouvés.
    
    Scanne :
    - Alma_toolset/*.luciform
    - Tools/*/documentation/luciforms/*.luciform
    """
    if self.indexed and not force_reindex:
        return
    
    # Scan des répertoires
    all_metadata = self.parser.scan_luciform_directories()
    
    # Injection de chaque outil
    for metadata in all_metadata:
        if metadata.get('tool_id'):
            self.register_tool(metadata)
    
    self.indexed = True
```

---

### **Étape 4 : Interface CLI et API** 🖥️
**Fichier :** `Core/tools_search_cli.py`

**Commandes CLI :**
```bash
# Recherche par type
python3 -m Core.tools_search_cli find-by-type divination

# Recherche par mot-clé
python3 -m Core.tools_search_cli find-by-keyword regex

# Recherche combinée
python3 -m Core.tools_search_cli search --type divination --level avancé

# Information sur un outil
python3 -m Core.tools_search_cli info regex_search_file

# Réindexation
python3 -m Core.tools_search_cli reindex
```

---

## 🔄 **Intégration avec l'Existant**

### **Modification du MemoryEngine Principal**
**Fichier :** `Core/Archivist/MemoryEngine/engine.py`

**Ajout d'une méthode d'extension :**
```python
def get_tool_search_extension(self):
    """Retourne l'extension de recherche d'outils."""
    if not hasattr(self, '_tool_extension'):
        from .tool_search_extension import ToolSearchExtension
        self._tool_extension = ToolSearchExtension(self)
    return self._tool_extension
```

### **Usage dans le Code Existant**
```python
# Initialisation
memory_engine = MemoryEngine()
tool_search = memory_engine.get_tool_search_extension()

# Recherche d'outils
divination_tools = tool_search.find_tools_by_type("divination")
regex_tools = tool_search.find_tools_by_keyword("regex")
```

---

## 🧪 **Tests et Validation**

### **Tests Unitaires :**
1. **Parser :** Extraction correcte des métadonnées
2. **Indexation :** Création des nœuds dans le bon namespace
3. **Recherche :** Résultats pertinents pour chaque critère
4. **Performance :** Temps de réponse < 100ms

### **Tests d'Intégration :**
1. **Indexation complète :** Tous les outils trouvés et indexés
2. **Recherche combinée :** Intersection correcte des critères
3. **Mise à jour :** Réindexation sans doublons

### **Cas de Test Prioritaires :**
```python
# Test 1: Recherche par type
assert len(find_tools_by_type("divination")) >= 2
assert "regex_search_file" in [t['tool_id'] for t in find_tools_by_type("divination")]

# Test 2: Recherche par mot-clé
regex_tools = find_tools_by_keyword("regex")
assert any(t['tool_id'] == "regex_search_file" for t in regex_tools)

# Test 3: Recherche combinée
advanced_divination = search_tools(tool_type="divination", level="avancé")
assert len(advanced_divination) >= 1
```

---

## 📁 **Structure de Fichiers Finale**

```
Core/
├── implementation/
│   └── luciform_tool_metadata_parser.py    # Étape 1
├── Archivist/MemoryEngine/
│   ├── engine.py                           # Modifié pour extension
│   └── tool_search_extension.py            # Étape 2
├── tools_search_cli.py                     # Étape 4
└── TOOL_SEARCH_SYSTEM_PLAN.md             # Ce fichier
```

---

## 🎯 **Prochaines Actions Immédiates**

### **Session Actuelle :**
1. ✅ Créer ce plan détaillé
2. 🔄 Implémenter `luciform_tool_metadata_parser.py`
3. 🔄 Créer `tool_search_extension.py`
4. 🔄 Tester l'indexation et recherche de base

### **Session Suivante :**
1. Interface CLI complète
2. Tests et optimisations
3. Documentation utilisateur
4. Intégration avec les daemons

---

## 💡 **Avantages de cette Approche**

### **✅ Réutilisation de l'Existant :**
- Utilise le MemoryEngine robuste et testé
- Pas de duplication de logique de stockage
- Bénéficie des backends (FileSystem, Neo4j)

### **✅ Séparation Claire :**
- Namespace `/tools/` dédié
- Pas de pollution des autres mémoires
- Structure hiérarchique par type

### **✅ Extensibilité :**
- Facile d'ajouter de nouveaux critères de recherche
- Support futur de recherche sémantique
- Intégration possible avec l'IA contextuelle

### **✅ Performance :**
- Index en mémoire pour recherches rapides
- Lazy loading des métadonnées complètes
- Cache des résultats fréquents

---

**⛧ Par Alma, qui organise le chaos en cosmos de recherche mystique ⛧**
