# 🤖 Guide Agent - Système de Recherche d'Outils Mystiques

**Pour :** Agents Conscients et Développeurs  
**Version :** 1.0  
**Date :** 2025-08-01  
**Créé par :** Alma, Architecte Démoniaque du Nexus Luciforme

---

## 🎯 **Introduction**

Ce guide vous apprend à utiliser le Système de Recherche d'Outils Mystiques pour découvrir et utiliser efficacement les 23 outils disponibles dans l'arsenal Alma.

### **Pourquoi ce système ?**
- **Découverte facile** des outils disponibles
- **Recherche intelligente** par multiple critères
- **Aide contextuelle** pour comprendre les types
- **Arsenal épuré** sans redondances

---

## 🚀 **Démarrage Rapide**

### **1. Initialisation du Système**
```python
from Core.Archivist.MemoryEngine.engine import MemoryEngine
from Core.Archivist.MemoryEngine.tool_search_extension import ToolSearchExtension

# Créer le MemoryEngine
memory_engine = MemoryEngine(backend_type="filesystem", base_path="./memory")

# Créer l'extension de recherche
tool_search = ToolSearchExtension(memory_engine)

# Indexer tous les outils (première fois)
count = tool_search.index_all_tools()
print(f"✅ {count} outils indexés et prêts à l'usage")
```

### **2. Obtenir de l'Aide**
```python
# Voir tous les types disponibles avec descriptions
help_text = tool_search.format_tool_types_help()
print(help_text)

# Ou juste la liste des types
types = tool_search.list_all_tool_types()
print(f"Types disponibles: {types}")
```

---

## 🔍 **Méthodes de Recherche**

### **1. Recherche par Type Mystique**

#### **Quand utiliser :**
Vous savez quel type d'opération vous voulez faire.

#### **Types disponibles :**
- **`divination`** - Révéler patterns cachés (regex, recherche)
- **`protection`** - Sauvegarder et protéger
- **`inscription`** - Créer nouveaux fichiers
- **`revelation`** - Lire fichiers existants
- **`metamorphosis`** - Transformer contenu
- **`filesystem`** - Manipuler répertoires
- **`modification`** - Éditer fichiers
- **`writing`** - Écrire contenu
- **`listing`** - Lister éléments

#### **Exemple :**
```python
# Trouver tous les outils de divination
divination_tools = tool_search.find_tools_by_type("divination")

for tool in divination_tools:
    print(f"🔮 {tool['tool_id']}: {tool['intent']}")
    print(f"   Niveau: {tool['level']}")
    print(f"   Keywords: {tool['keywords']}")
    print()
```

### **2. Recherche par Mot-clé**

#### **Quand utiliser :**
Vous cherchez une fonctionnalité spécifique.

#### **Exemples courants :**
```python
# Outils pour regex
regex_tools = tool_search.find_tools_by_keyword("regex")

# Outils pour fichiers
file_tools = tool_search.find_tools_by_keyword("file")

# Outils pour backup
backup_tools = tool_search.find_tools_by_keyword("backup")

# Outils pour répertoires
dir_tools = tool_search.find_tools_by_keyword("directory")
```

### **3. Recherche par Niveau**

#### **Quand utiliser :**
Vous voulez des outils adaptés à votre niveau de complexité.

#### **Niveaux disponibles :**
- **`fondamental`** 🟢 - Outils simples et sûrs
- **`intermédiaire`** 🟡 - Outils moyens
- **`avancé`** 🔴 - Outils complexes et puissants

#### **Exemple :**
```python
# Outils pour débutants
basic_tools = tool_search.find_tools_by_level("fondamental")

# Outils avancés
advanced_tools = tool_search.find_tools_by_level("avancé")
```

### **4. Recherche par Intention**

#### **Quand utiliser :**
Vous décrivez ce que vous voulez faire en langage naturel.

#### **Exemples :**
```python
# Chercher des outils pour sauvegarder
backup_tools = tool_search.find_tools_by_intent("sauvegarder fichier")

# Chercher des outils pour rechercher
search_tools = tool_search.find_tools_by_intent("rechercher pattern")

# Chercher des outils pour créer
create_tools = tool_search.find_tools_by_intent("créer nouveau fichier")
```

### **5. Recherche Combinée**

#### **Quand utiliser :**
Vous voulez affiner votre recherche avec plusieurs critères.

#### **Exemples :**
```python
# Outils divination avancés avec regex
advanced_regex = tool_search.search_tools(
    tool_type="divination",
    keyword="regex",
    level="avancé"
)

# Outils fondamentaux pour fichiers
basic_file_tools = tool_search.search_tools(
    keyword="file",
    level="fondamental",
    limit=5
)

# Outils pour créer avec inscription
creation_tools = tool_search.search_tools(
    tool_type="inscription",
    intent="créer nouveau"
)
```

---

## 📖 **Obtenir des Informations Détaillées**

### **Information Complète d'un Outil**
```python
# Obtenir toutes les infos d'un outil
tool_info = tool_search.get_tool_info("regex_search_file")

print(f"ID: {tool_info['tool_id']}")
print(f"Type: {tool_info['type']}")
print(f"Niveau: {tool_info['level']}")
print(f"Intent: {tool_info['intent']}")
print(f"Signature: {tool_info['signature']}")
print(f"Keywords: {tool_info['keywords']}")
print(f"Usage: {tool_info['usage_context']}")
```

### **Statistiques Globales**
```python
# Voir les statistiques de l'arsenal
stats = tool_search.get_tools_statistics()

print(f"Total outils: {stats['total_tools']}")
print(f"Par type: {stats['by_type']}")
print(f"Par niveau: {stats['by_level']}")
print(f"Keywords uniques: {stats['unique_keywords']}")
```

---

## 🎭 **Guide des Types Mystiques**

### **🔮 DIVINATION (4 outils)**
*"Révéler les patterns cachés et scruter les mystères du code"*

**Quand utiliser :** Recherche, analyse de patterns, exploration de code

**Outils principaux :**
- `regex_search_file` 🔴 - Recherche regex avancée
- `find_text_in_project` 🟡 - Recherche dans tout le projet
- `locate_text_sigils` 🔴 - Trouver numéros de ligne
- `scry_for_text` 🟡 - Recherche avec contexte

### **🛡️ PROTECTION (1 outil)**
*"Garder et sauvegarder les grimoires sacrés contre la corruption"*

**Quand utiliser :** Sauvegardes, protection des données

**Outils :**
- `backup_creator` 🟢 - Créer sauvegardes horodatées

### **📝 INSCRIPTION (2 outils)**
*"Graver de nouveaux grimoires dans la réalité"*

**Quand utiliser :** Créer nouveaux fichiers

**Outils :**
- `safe_create_file` 🟢 - Créer fichier sécurisé
- `safe_overwrite_file` 🟡 - Réécrire fichier complet

### **👁️ REVELATION (1 outil)**
*"Révéler les secrets contenus dans les fichiers existants"*

**Quand utiliser :** Lire contenu de fichiers

**Outils :**
- `safe_read_file_content` 🟢 - Lire fichier sécurisé

### **🔄 METAMORPHOSIS (1 outil)**
*"Transformer et métamorphoser le contenu existant"*

**Quand utiliser :** Remplacer texte dans fichiers

**Outils :**
- `safe_replace_text_in_file` 🟡 - Remplacer texte

### **📁 FILESYSTEM (3 outils)**
*"Manipuler la structure mystique des répertoires"*

**Quand utiliser :** Gestion de répertoires

**Outils :**
- `safe_create_directory` 🟢 - Créer répertoire
- `safe_delete_directory` 🔴 - Supprimer répertoire
- `rename_project_entity` 🔴 - Renommer fichier/dossier

---

## 💡 **Cas d'Usage Courants**

### **Scenario 1 : "Je veux chercher du texte"**
```python
# Voir les outils de recherche
search_tools = tool_search.find_tools_by_type("divination")

# Ou par intention
search_tools = tool_search.find_tools_by_intent("rechercher texte")

# Pour un fichier spécifique
regex_tool = tool_search.get_tool_info("regex_search_file")

# Pour tout le projet
project_tool = tool_search.get_tool_info("find_text_in_project")
```

### **Scenario 2 : "Je veux créer un fichier"**
```python
# Outils de création
creation_tools = tool_search.find_tools_by_type("inscription")

# Outil simple pour débutant
basic_tools = tool_search.search_tools(
    tool_type="inscription",
    level="fondamental"
)
```

### **Scenario 3 : "Je ne sais pas quoi utiliser"**
```python
# Voir l'aide complète
help_text = tool_search.format_tool_types_help()
print(help_text)

# Voir tous les outils par niveau
basic = tool_search.find_tools_by_level("fondamental")
print(f"Outils simples: {[t['tool_id'] for t in basic]}")
```

### **Scenario 4 : "Je veux faire une sauvegarde"**
```python
# Recherche par intention
backup_tools = tool_search.find_tools_by_intent("sauvegarde backup")

# Ou par type
protection_tools = tool_search.find_tools_by_type("protection")
```

---

## ⚠️ **Bonnes Pratiques**

### **1. Toujours Indexer d'Abord**
```python
# Première utilisation
tool_search.index_all_tools()

# Réindexation si nouveaux outils
tool_search.index_all_tools(force_reindex=True)
```

### **2. Utiliser l'Aide Contextuelle**
```python
# Quand vous êtes perdus
help_text = tool_search.format_tool_types_help()
print(help_text)
```

### **3. Commencer Simple**
```python
# Préférer les outils fondamentaux
basic_tools = tool_search.find_tools_by_level("fondamental")
```

### **4. Vérifier les Infos Complètes**
```python
# Avant d'utiliser un outil
tool_info = tool_search.get_tool_info("nom_outil")
print(f"Usage: {tool_info['usage_context']}")
print(f"Signature: {tool_info['signature']}")
```

---

## 🔧 **Dépannage**

### **Problème : Aucun outil trouvé**
```python
# Vérifier l'indexation
count = tool_search.index_all_tools(force_reindex=True)
print(f"Outils indexés: {count}")

# Vérifier les types disponibles
types = tool_search.list_all_tool_types()
print(f"Types: {types}")
```

### **Problème : Recherche trop large**
```python
# Utiliser la recherche combinée
specific_tools = tool_search.search_tools(
    tool_type="divination",
    level="fondamental",
    limit=3
)
```

### **Problème : Ne comprend pas un type**
```python
# Voir les descriptions
types_info = tool_search.list_tool_types_with_descriptions()
print(types_info['divination']['description'])
```

---

## 🎉 **Conclusion**

Le Système de Recherche d'Outils Mystiques vous donne accès à un arsenal de 23 outils épurés et bien documentés. Utilisez l'aide contextuelle, commencez par les outils fondamentaux, et n'hésitez pas à explorer !

**🖤✨ Que la recherche mystique guide vos créations ! ✨🖤**

---

**⛧ Guide créé par Alma pour les agents en quête de sagesse ⛧**
