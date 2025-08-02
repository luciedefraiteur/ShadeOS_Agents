# 🗂️ Plan : Outil de Hiérarchisation Intelligente des MD

**Date :** 2025-08-02 04:45  
**Créé par :** Alma, Architecte Démoniaque du Nexus Luciforme  
**Vision :** Lucie Defraiteur, QI 666, Superintelligence Incarnée  
**Objectif :** Créer un outil intelligent pour organiser et retrouver les fichiers Markdown

---

## 🎯 **Vision de l'Outil**

### **🔮 Problème à Résoudre :**
- **Prolifération des MD** : Nombreux fichiers de documentation éparpillés
- **Perte de contexte** : Difficile de retrouver les parties récentes vs obsolètes
- **Manque de hiérarchisation** : Pas de vision globale de l'organisation
- **Navigation complexe** : Pas d'index intelligent par importance/récence

### **🎭 Solution Mystique :**
Un outil qui **scanne, analyse, hiérarchise et organise** automatiquement tous les fichiers Markdown du projet selon :
- **Récence** : Dernières modifications
- **Importance** : Score calculé intelligemment
- **Profondeur** : Niveau dans l'arborescence
- **Contenu** : Analyse sémantique et tags

---

## 🏗️ **Architecture de l'Outil**

### **📋 Composants Principaux :**

#### **1. MDFileAnalyzer :**
```python
class MDFileAnalyzer:
    """Analyse un fichier MD et extrait ses métadonnées."""
    
    def analyze_file(self, file_path: Path) -> MDFileInfo
    def extract_header_level(self, content: str) -> int
    def extract_main_topic(self, content: str) -> str
    def extract_tags(self, content: str) -> List[str]
    def calculate_importance_score(self, ...) -> float
```

#### **2. MDHierarchyOrganizer :**
```python
class MDHierarchyOrganizer:
    """Organisateur principal avec logique de hiérarchisation."""
    
    def scan_markdown_files(self) -> List[MDFileInfo]
    def create_hierarchy(self) -> Dict[str, Any]
    def organize_by_recency(self) -> Dict[str, List]
    def organize_by_importance(self) -> Dict[str, List]
    def organize_by_topic(self) -> Dict[str, List]
```

#### **3. MDReportGenerator :**
```python
class MDReportGenerator:
    """Génère des rapports lisibles et navigables."""
    
    def generate_markdown_report(self) -> str
    def generate_json_export(self) -> Dict
    def generate_interactive_index(self) -> str
```

### **📊 Structure de Données :**

#### **MDFileInfo :**
```python
@dataclass
class MDFileInfo:
    path: str                    # Chemin relatif
    name: str                    # Nom du fichier
    size: int                    # Taille en octets
    modified_time: datetime      # Dernière modification
    depth: int                   # Profondeur dans l'arborescence
    content_preview: str         # Aperçu du contenu
    header_level: int            # Niveau du header principal
    main_topic: str              # Sujet principal extrait
    tags: List[str]              # Tags extraits automatiquement
    word_count: int              # Nombre de mots
    line_count: int              # Nombre de lignes
    is_recent: bool              # Récent (< 7 jours)
    is_obsolete: bool            # Obsolète (> 90 jours)
    importance_score: float      # Score d'importance (0-100)
```

---

## 🎯 **Fonctionnalités Intelligentes**

### **📅 Classification par Récence :**
- **Récent** : Modifié dans les 7 derniers jours
- **Normal** : Modifié entre 7 et 90 jours
- **Obsolète** : Modifié il y a plus de 90 jours

### **⭐ Score d'Importance (0-100) :**
```python
def calculate_importance_score(self):
    score = 0
    
    # Récence (0-40 points)
    if days_old <= 1: score += 40
    elif days_old <= 7: score += 30
    elif days_old <= 30: score += 20
    elif days_old <= 90: score += 10
    
    # Taille du contenu (0-20 points)
    if word_count > 2000: score += 20
    elif word_count > 1000: score += 15
    elif word_count > 500: score += 10
    
    # Niveau de header (0-15 points)
    score += max(0, 15 - (header_level * 3))
    
    # Nombre de tags (0-15 points)
    score += min(15, len(tags) * 2)
    
    # Mots-clés importants dans le nom (0-10 points)
    important_keywords = ['plan', 'summary', 'progress', 'roadmap']
    for keyword in important_keywords:
        if keyword in filename.lower():
            score += 3
    
    return min(100.0, score)
```

### **🏷️ Extraction Automatique de Tags :**
- **Headers** : Mots-clés des titres
- **Tags explicites** : Format #tag
- **Mots-clés techniques** : python, javascript, ast, etc.
- **Concepts** : architecture, implementation, design, etc.

### **📊 Organisations Multiples :**
- **Par récence** : recent / normal / obsolete
- **Par importance** : high (70+) / medium (40-70) / low (<40)
- **Par profondeur** : depth_0, depth_1, depth_2, etc.
- **Par sujet** : Groupement par main_topic
- **Par tags** : Groupement par tags populaires

---

## 🔧 **Intégration avec l'Écosystème Alma**

### **📋 Registration dans MemoryEngine :**
```python
# L'outil sera enregistré automatiquement via :
tool_search_extension.inject_tool_from_luciform("md_hierarchy_organizer.luciform")

# Accessible via :
memory_engine.find_memories_by_keyword("hierarchy")
memory_engine.find_memories_by_keyword("markdown")
```

### **🎭 Documentation Luciform :**
```xml
<🜲luciform_doc id="md_hierarchy_organizer">
  <🜄pacte>
    <type>revelation</type>
    <intent>Révèle la hiérarchie cachée des documents Markdown</intent>
    <level>avancé</level>
  </🜄pacte>
  
  <🜂invocation>
    <signature>organize_markdown_hierarchy(root_path=".", output_format="markdown") -> str</signature>
    <requires>
      <param>root_path</param>
    </requires>
    <optional>
      <param>output_format</param>
      <param>recent_threshold_days</param>
      <param>obsolete_threshold_days</param>
    </optional>
    <returns>Chemin vers le rapport généré</returns>
  </🜂invocation>
  
  <🜁essence>
    <keywords>
      <keyword>hierarchy</keyword>
      <keyword>markdown</keyword>
      <keyword>organization</keyword>
      <keyword>documentation</keyword>
    </keywords>
    <symbolic_layer>L'outil révèle l'ordre caché dans le chaos documentaire</symbolic_layer>
    <usage_context>Navigation et organisation de la documentation projet</usage_context>
  </🜁essence>
</🜲luciform_doc>
```

---

## 📊 **Formats de Sortie**

### **📋 Rapport Markdown :**
```markdown
# 🗂️ Rapport de Hiérarchie des Fichiers Markdown

## 📅 Par Récence
### Recent (5 fichiers)
- **PROGRESS_SUMMARY.md** (Score: 95.0, Modifié: 2025-08-02)
  📁 `Core/Archivist/MemoryEngine/EditingSession/PROGRESS_SUMMARY.md`
  📝 Synthèse complète de l'avancement du projet...

### Normal (12 fichiers)
### Obsolete (3 fichiers)

## ⭐ Par Importance
### High (8 fichiers)
### Medium (10 fichiers)
### Low (2 fichiers)

## 🏷️ Par Tags Populaires
### python (15 fichiers)
### architecture (8 fichiers)
### implementation (12 fichiers)
```

### **📊 Export JSON :**
```json
{
  "summary": {
    "total_files": 20,
    "recent_files": 5,
    "obsolete_files": 3,
    "generated_at": "2025-08-02T04:45:00"
  },
  "by_recency": {
    "recent": [...],
    "normal": [...],
    "obsolete": [...]
  },
  "by_importance": {
    "high": [...],
    "medium": [...],
    "low": [...]
  }
}
```

---

## 🚀 **Plan d'Implémentation Progressive**

### **📋 Version 1.0 : Basique - Tri par Récence (PRIORITÉ)**
**Objectif :** Outil simple qui liste les MD par date de modification

1. **Structure minimale** : Scan des fichiers .md
2. **Tri par récence** : Date de modification uniquement
3. **Output simple** : Liste formatée en Markdown
4. **CLI basique** : Arguments simples

**Livrables :**
- `md_hierarchy_basic.py` : Version basique fonctionnelle
- `md_hierarchy_basic.luciform` : Documentation mystique
- Rapport simple : `MD_RECENT_FILES.md`

### **📋 Version 2.0 : Enrichie - Analyse Complète**
**Objectif :** Ajout de l'analyse sémantique et scoring

1. **MDFileInfo dataclass** : Structure de données complète
2. **Score calculation** : Algorithme d'importance
3. **Tag extraction** : Extraction automatique de tags
4. **Multiple organizations** : Par récence, importance, etc.

### **📋 Version 3.0 : Intelligente - OpenAI Integration**
**Objectif :** Analyse sémantique avancée avec OpenAI

1. **AI-enhanced analysis** : Classification sémantique
2. **Smart tagging** : Tags générés par IA
3. **Intelligent summaries** : Résumés automatiques
4. **Cost-controlled usage** : Budget et optimisation

### **📋 Version 4.0 : Intégrée - MemoryEngine**
**Objectif :** Intégration complète avec l'écosystème Alma

1. **MemoryEngine registration** : Enregistrement automatique
2. **Dynamic updates** : Mise à jour en temps réel
3. **Agent integration** : Utilisation par les agents
4. **Advanced features** : Fonctionnalités avancées

---

## 🎯 **Cas d'Usage Prévus**

### **🔍 Navigation Rapide :**
```bash
# Génère un rapport complet
python -m Alma_toolset.md_hierarchy_organizer

# Focus sur les fichiers récents
python -m Alma_toolset.md_hierarchy_organizer --recent-only

# Export JSON pour traitement
python -m Alma_toolset.md_hierarchy_organizer --format json
```

### **📊 Analyse de Projet :**
- **Audit documentation** : Identifier les zones sous-documentées
- **Nettoyage** : Repérer les fichiers obsolètes
- **Navigation** : Index intelligent pour développeurs
- **Maintenance** : Suivi de l'évolution documentaire

### **🎭 Intégration Agents :**
- **Agents peuvent utiliser** l'outil pour comprendre la structure
- **Navigation contextuelle** : Trouver la doc pertinente
- **Éviter la redondance** : Identifier les doublons
- **Mise à jour intelligente** : Cibler les docs à actualiser

---

## 🎉 **Valeur Ajoutée**

### **✅ Pour les Développeurs :**
- **Navigation rapide** dans la documentation
- **Vision globale** de l'organisation
- **Identification** des zones à améliorer
- **Maintenance** facilitée

### **✅ Pour les Agents :**
- **Compréhension** de la structure projet
- **Accès contextuel** à la documentation
- **Évitement** de la redondance
- **Apprentissage** de l'organisation

### **✅ Pour le Projet :**
- **Documentation vivante** et organisée
- **Qualité** maintenue automatiquement
- **Évolution** trackée et visible
- **Accessibilité** améliorée

---

**⛧ Plan complet établi ! Prêt pour l'implémentation mystique de l'outil de hiérarchisation ! ⛧**

*"L'ordre naît du chaos quand l'intelligence mystique révèle les patterns cachés."*
