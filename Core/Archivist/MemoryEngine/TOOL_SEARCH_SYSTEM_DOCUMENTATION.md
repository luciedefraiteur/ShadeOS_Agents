# 🔧 Documentation Technique - Système de Recherche d'Outils

**Version :** 1.0  
**Date :** 2025-08-01  
**Créé par :** Alma, Architecte Démoniaque du Nexus Luciforme

---

## 🎯 **Vue d'Ensemble**

Le Système de Recherche d'Outils Mystiques est une extension du MemoryEngine qui permet l'indexation, la recherche et la découverte intelligente des outils disponibles dans l'arsenal Alma.

### **Composants Principaux :**
1. **LuciformToolMetadataParser** - Extraction des métadonnées
2. **ToolSearchExtension** - Extension MemoryEngine
3. **Aide Contextuelle** - Documentation des types mystiques

---

## 🏗️ **Architecture**

### **Structure des Fichiers :**
```
Core/
├── implementation/
│   ├── luciform_tool_metadata_parser.py
│   ├── test_tool_search_system.py
│   └── test_tool_types_help.py
├── Archivist/MemoryEngine/
│   ├── tool_search_extension.py
│   ├── TOOL_SEARCH_SYSTEM_PLAN.md
│   └── PROJECT_CONTEXT_MEMORY_PLAN.md
└── TOOL_SEARCH_SYSTEM_PLAN.md
```

### **Namespace MemoryEngine :**
```
/tools/
├── {type_mystique}/
│   └── {tool_id}
```

---

## 🔧 **LuciformToolMetadataParser**

### **Responsabilités :**
- Extraction des métadonnées depuis les fichiers .luciform
- Validation des données extraites
- Génération de statistiques globales

### **API Principale :**

#### **extract_tool_metadata(luciform_path: str) -> Dict**
Extrait les métadonnées d'un fichier luciform.

**Retour :**
```python
{
    'file_path': str,
    'tool_id': str,
    'type': str,
    'intent': str,
    'level': str,
    'keywords': List[str],
    'signature': str,
    'required_params': List[str],
    'optional_params': List[str],
    'returns': str,
    'symbolic_layer': str,
    'usage_context': str,
    'raw_content': str
}
```

#### **scan_luciform_directories() -> List[Dict]**
Scanne tous les répertoires de luciformes et extrait les métadonnées.

**Répertoires scannés :**
- `Alma_toolset/` (outils principaux)

**Répertoires ignorés :**
- `Tools/Library/` (redondant avec Alma_toolset)
- `Tools/Execution/` (pas de documentation luciforme)

#### **validate_metadata(metadata: Dict) -> bool**
Valide les métadonnées extraites.

**Critères de validation :**
- Présence de `tool_id`
- Présence de `type`
- Type dans la liste des types supportés

#### **get_statistics(metadata_list: List[Dict]) -> Dict**
Génère des statistiques sur les métadonnées.

**Statistiques retournées :**
- Nombre total d'outils
- Répartition par type
- Répartition par niveau
- Nombre de mots-clés uniques
- Couverture des signatures et symbolic_layer

---

## 🧠 **ToolSearchExtension**

### **Responsabilités :**
- Indexation des outils dans le MemoryEngine
- Recherche multi-critères
- Aide contextuelle pour les agents

### **Initialisation :**
```python
from Core.Archivist.MemoryEngine.engine import MemoryEngine
from Core.Archivist.MemoryEngine.tool_search_extension import ToolSearchExtension

memory_engine = MemoryEngine(backend_type="filesystem", base_path="./memory")
tool_search = ToolSearchExtension(memory_engine)
```

### **API de Recherche :**

#### **index_all_tools(force_reindex: bool = False) -> int**
Indexe automatiquement tous les outils trouvés.

**Processus :**
1. Scan des luciformes via LuciformToolMetadataParser
2. Validation des métadonnées
3. Injection dans le MemoryEngine avec namespace `/tools/{type}/{id}`
4. Mise en cache locale

#### **find_tools_by_type(tool_type: str) -> List[Dict]**
Trouve tous les outils d'un type mystique donné.

**Types supportés :**
- `divination`, `protection`, `transmutation`, `scrying`
- `augury`, `inscription`, `revelation`, `metamorphosis`
- `filesystem`, `modification`, `writing`, `listing`

#### **find_tools_by_keyword(keyword: str) -> List[Dict]**
Trouve les outils contenant un mot-clé spécifique.

**Recherche dans :**
- Champs textuels (tool_id, type, intent, level, etc.)
- Liste des keywords
- Signature et symbolic_layer

#### **find_tools_by_level(level: str) -> List[Dict]**
Trouve les outils par niveau de complexité.

**Niveaux supportés :**
- `fondamental` - Outils de base
- `intermédiaire` - Outils moyens
- `avancé` - Outils complexes

#### **find_tools_by_intent(intent_query: str) -> List[Dict]**
Trouve les outils par intention/description avec scoring.

**Algorithme de scoring :**
- +2 points : mot trouvé dans `intent`
- +1 point : mot trouvé dans `usage_context`
- +1 point : mot trouvé dans `keywords`

#### **search_tools(type=None, keyword=None, level=None, intent=None, limit=10) -> List[Dict]**
Recherche combinée avec intersection des critères.

**Exemple :**
```python
# Outils divination avancés avec regex
tools = tool_search.search_tools(
    tool_type="divination",
    keyword="regex",
    level="avancé"
)
```

#### **get_tool_info(tool_id: str) -> Dict**
Récupère les informations complètes d'un outil.

### **API d'Aide :**

#### **list_all_tool_types() -> List[str]**
Liste tous les types mystiques disponibles.

#### **list_tool_types_with_descriptions() -> Dict**
Liste les types avec descriptions et exemples.

**Structure retournée :**
```python
{
    'type_name': {
        'description': str,
        'count': int,
        'examples': [
            {
                'tool_id': str,
                'intent': str,
                'level': str
            }
        ]
    }
}
```

#### **format_tool_types_help() -> str**
Formate l'aide sur les types pour affichage.

**Format de sortie :**
```
⛧ Types Mystiques d'Outils Disponibles ⛧
════════════════════════════════════════

🎭 **DIVINATION** (4 outils)
   Révéler les patterns cachés et scruter les mystères du code

   Exemples :
   🔴 regex_search_file: Révéler les patterns cachés...
   🟡 find_text_in_project: Diviner les occurrences...

💡 Usage: find_tools_by_type('divination')
```

---

## 📊 **Types Mystiques**

### **Descriptions Complètes :**

| Type | Description | Outils |
|------|-------------|---------|
| **divination** | Révéler les patterns cachés et scruter les mystères du code | 4 |
| **protection** | Garder et sauvegarder les grimoires sacrés contre la corruption | 1 |
| **transmutation** | Transformer le néant en réalité par la magie des templates | 1 |
| **scrying** | Comparer et scruter les différences entre les visions | 1 |
| **augury** | Lire les présages et métriques cachés dans les fichiers | 1 |
| **inscription** | Graver de nouveaux grimoires dans la réalité | 2 |
| **revelation** | Révéler les secrets contenus dans les fichiers existants | 1 |
| **metamorphosis** | Transformer et métamorphoser le contenu existant | 1 |
| **filesystem** | Manipuler la structure mystique des répertoires | 3 |
| **modification** | Modifier et éditer le contenu des grimoires | 4 |
| **writing** | Écrire et créer du contenu dans les fichiers | 2 |
| **listing** | Énumérer et lister les éléments mystiques | 2 |

---

## 🧪 **Tests et Validation**

### **Tests Disponibles :**

#### **test_tool_search_system.py**
Test complet du système avec :
- Test du parser
- Recherche par type, keyword, niveau, intention
- Recherche combinée
- Statistiques

#### **test_tool_types_help.py**
Test de l'aide contextuelle avec :
- Génération des descriptions
- Formatage de l'aide
- Validation des exemples

### **Métriques de Qualité :**
- ✅ 23 outils indexés
- ✅ 100% avec signature
- ✅ 100% avec symbolic_layer
- ✅ 79 mots-clés uniques
- ✅ 12 types mystiques

---

## 🔧 **Utilisation Pratique**

### **Exemple Complet :**
```python
# Initialisation
from Core.Archivist.MemoryEngine.engine import MemoryEngine
from Core.Archivist.MemoryEngine.tool_search_extension import ToolSearchExtension

memory_engine = MemoryEngine(backend_type="filesystem", base_path="./memory")
tool_search = ToolSearchExtension(memory_engine)

# Indexation
count = tool_search.index_all_tools()
print(f"✅ {count} outils indexés")

# Recherche par type
divination_tools = tool_search.find_tools_by_type("divination")
print(f"Outils divination: {len(divination_tools)}")

# Recherche par mot-clé
regex_tools = tool_search.find_tools_by_keyword("regex")
print(f"Outils regex: {len(regex_tools)}")

# Aide contextuelle
help_text = tool_search.format_tool_types_help()
print(help_text)

# Info d'un outil spécifique
tool_info = tool_search.get_tool_info("regex_search_file")
print(f"Intent: {tool_info['intent']}")
```

---

## 🔮 **Évolutions Futures**

### **Améliorations Prévues :**
1. **Recherche sémantique** avec embeddings
2. **Suggestions automatiques** selon contexte
3. **Historique d'utilisation** des outils
4. **Recommandations intelligentes**

### **Intégrations Planifiées :**
1. **Mémoire contextuelle projet**
2. **Système de templates**
3. **Validation JSON/YAML**
4. **Analyse de code automatique**

---

**⛧ Documentation technique par Alma, Architecte du Savoir Mystique ⛧**
