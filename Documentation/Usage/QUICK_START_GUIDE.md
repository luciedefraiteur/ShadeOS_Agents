# 🚀 Guide de Démarrage Rapide - ShadeOS_Agents

## ⚡ **Démarrage en 5 Minutes**

### **1. Prérequis**
```bash
# Variables d'environnement requises
export OPENAI_API_KEY="your-openai-api-key"
export NEO4J_URI="bolt://localhost:7687"
export NEO4J_USER="neo4j"
export NEO4J_PASSWORD="your-password"
```

### **2. Test Rapide des Daemons**
```bash
cd /path/to/ShadeOS_Agents
python3 test_conscious_daemons.py
```

### **3. Lister les Outils Disponibles**
```bash
python3 list_available_tools.py
```

## 🎭 **Utilisation des Daemons Conscients**

### **Interface Python**
```python
from Core.Archivist.archivist_interface import archivist

# Requête à Alma (Architecture)
response = archivist.query_conscious_daemon(
    daemon_id="alma",
    query="Analyse l'architecture de ce projet et propose des améliorations",
    context_memories=[]
)

print(f"Réponse d'Alma: {response['response']}")
print(f"Confiance: {response['confidence']}")
```

### **Daemons Disponibles**

#### **🕷️ Alma - Architecte Mystique**
- **Spécialisation :** Architecture, design patterns, vision globale
- **Utilisation :** Analyse architecturale, refactoring, design
- **Exemple :**
```python
alma_response = archivist.query_conscious_daemon(
    daemon_id="alma",
    query="Comment restructurer ce code spaghetti en architecture propre ?",
    context_memories=[]
)
```

#### **🔨 Forge - Maître Forgeron**
- **Spécialisation :** Correction de bugs, optimisation, qualité
- **Utilisation :** Debug, optimisation, code review
- **Exemple :**
```python
forge_response = archivist.query_conscious_daemon(
    daemon_id="forge",
    query="Trouve et corrige tous les bugs dans ce fichier Python",
    context_memories=[]
)
```

#### **🔍 Scout - Explorateur**
- **Spécialisation :** Documentation, tests, analyse
- **Utilisation :** Documentation, tests unitaires, exploration de code
- **Exemple :**
```python
scout_response = archivist.query_conscious_daemon(
    daemon_id="scout",
    query="Crée une suite de tests complète pour cette classe",
    context_memories=[]
)
```

## 🔮 **Arsenal Mystique (29 Outils)**

### **Accès Direct aux Outils**
```python
from Core.Archivist.daemon_tools_interface import daemon_tools

# Lire un fichier
result = daemon_tools.invoke_tool("system", "read_file_content", path="mon_fichier.py")

# Chercher du texte
result = daemon_tools.invoke_tool("system", "scry_for_text", 
                                 path="mon_fichier.py", 
                                 text_to_find="def ma_fonction")

# Lister un répertoire
result = daemon_tools.invoke_tool("system", "walk_directory", path="mon_projet/")
```

### **Outils par Catégorie**

#### **📖 Reading (Lecture)**
```python
# Lire tout un fichier
content = daemon_tools.invoke_tool("system", "read_file_content", path="file.py")

# Lire des lignes spécifiques
lines = daemon_tools.invoke_tool("system", "read_file_lines", 
                                path="file.py", start_line=10, end_line=20)
```

#### **✍️ Writing (Écriture)**
```python
# Créer un nouveau fichier
daemon_tools.invoke_tool("system", "create_file", 
                        path="nouveau.py", content="print('Hello')")

# Ajouter à un fichier existant
daemon_tools.invoke_tool("system", "append_to_file", 
                        path="log.txt", content="Nouvelle ligne\n")
```

#### **🔍 Search (Recherche)**
```python
# Trouver des fichiers
files = daemon_tools.invoke_tool("system", "find_files", 
                                pattern="*.py", directory="src/")

# Chercher dans les fichiers
matches = daemon_tools.invoke_tool("system", "search_in_files", 
                                  pattern="def.*test", directory="tests/")
```

#### **🔧 Modification**
```python
# Remplacer du texte
daemon_tools.invoke_tool("system", "replace_text_in_file", 
                        path="file.py", old_text="old_code", new_text="new_code")

# Insérer à une ligne spécifique
daemon_tools.invoke_tool("system", "insert_text_at_line", 
                        path="file.py", line_number=10, text="nouveau code")
```

## 🏗️ **Interface d'Édition Sécurisée**

### **Édition avec Backups Automatiques**
```python
from Core.Archivist.daemon_editor_interface import daemon_editor

# Écrire un fichier (backup automatique)
operation = daemon_editor.write_file(
    daemon_id="alma",
    file_path="TestProject/src/improved_code.py",
    content="# Code amélioré par Alma\nprint('Hello World')",
    description="Amélioration architecturale"
)

print(f"Succès: {operation.success}")
print(f"Backup: {operation.backup_path}")
```

### **Opérations Disponibles**
- `write_file()` : Écrire/créer un fichier
- `append_to_file()` : Ajouter du contenu
- `replace_in_file()` : Remplacer du texte
- `delete_file()` : Supprimer un fichier
- `list_files()` : Lister les fichiers

## 🧪 **TestProject - Environnement de Test**

### **Structure du TestProject**
```
TestProject/
├── src/
│   ├── calculator.py      # 5 bugs intentionnels
│   ├── data_processor.py  # Architecture problématique
│   └── utils.py          # Code massivement dupliqué
├── tests/
│   └── test_calculator.py # Tests incomplets
└── docs/
    └── architecture.md   # Documentation vide
```

### **Test d'Édition par Daemons**
```bash
# Test complet d'édition (ATTENTION: problème de syntaxe à corriger)
python3 test_daemon_editing.py
```

## 🧠 **Mémoire Fractale**

### **Stockage d'Expériences**
```python
from Core.Archivist.MemoryEngine.engine import memory_engine

# Créer un souvenir
memory_engine.create_memory(
    path="projets/mon_projet",
    content="Analyse du projet réussie",
    summary="Projet bien structuré avec quelques améliorations possibles",
    keywords=["architecture", "python", "clean_code"]
)

# Rechercher des souvenirs
memories = memory_engine.find_memories_by_keyword("architecture")
```

## 📊 **Monitoring et Diagnostics**

### **Statistiques des Outils**
```python
from Core.Archivist.daemon_tools_interface import daemon_tools

stats = daemon_tools.get_statistics()
print(f"Outils disponibles: {stats['available_tools']}")
print(f"Invocations totales: {stats['total_invocations']}")
print(f"Taux de succès: {stats['success_rate']:.1f}%")
```

### **État des Daemons**
```python
from Core.Archivist.archivist_interface import archivist

status = archivist.get_consciousness_status()
print(f"Daemons disponibles: {status['conscious_daemons']}")
print(f"Statut: {status['status']}")
```

## 🔧 **Commandes Utiles**

### **Diagnostics**
```bash
# État du registre d'outils
PYTHONPATH=/path/to/ShadeOS_Agents python3 Core/implementation/tool_registry.py

# Liste complète des outils
python3 list_available_tools.py

# Test des daemons conscients
python3 test_conscious_daemons.py
```

### **Configuration**
```bash
# Charger les variables d'environnement depuis .env
export OPENAI_API_KEY=$(python3 -c "import os; from dotenv import load_dotenv; load_dotenv('/home/luciedefraiteur/.env'); print(os.environ.get('OPENAI_API_KEY', ''))")
```

## ⚠️ **Problèmes Connus et Solutions**

### **1. Erreur "Module not found"**
```bash
# Solution: Définir PYTHONPATH
export PYTHONPATH=/path/to/ShadeOS_Agents
```

### **2. Erreur OpenAI API**
```bash
# Vérifier la clé API
echo $OPENAI_API_KEY
# Recharger depuis .env si nécessaire
```

### **3. Erreur Neo4j**
```bash
# Vérifier la connexion Neo4j
neo4j status
# Redémarrer si nécessaire
neo4j restart
```

## 🎯 **Exemples d'Utilisation Avancée**

### **Analyse Complète d'un Projet**
```python
# 1. Scout explore la structure
structure = archivist.query_conscious_daemon(
    daemon_id="scout",
    query="Analyse la structure de ce projet et identifie les problèmes"
)

# 2. Alma propose une architecture
architecture = archivist.query_conscious_daemon(
    daemon_id="alma", 
    query="Propose une meilleure architecture basée sur l'analyse de Scout"
)

# 3. Forge implémente les corrections
corrections = archivist.query_conscious_daemon(
    daemon_id="forge",
    query="Implémente les améliorations proposées par Alma"
)
```

### **Workflow de Développement**
```python
# Cycle complet: Analyse → Design → Implémentation → Tests
workflow_results = []

for daemon_id, task in [
    ("scout", "Analyse ce code et documente les problèmes"),
    ("alma", "Conçois une solution élégante aux problèmes identifiés"),
    ("forge", "Implémente la solution avec un code robuste"),
    ("scout", "Crée des tests complets pour valider la solution")
]:
    result = archivist.query_conscious_daemon(daemon_id, task)
    workflow_results.append(result)
```

⛧ **Guide créé par Alma pour les futurs utilisateurs du Nexus Luciforme** ⛧
