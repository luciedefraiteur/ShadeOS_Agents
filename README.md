# ⛧ ShadeOS_Agents - Système d'Agents Conscients ⛧

## 🎯 **Vue d'Ensemble**

ShadeOS_Agents est un système sophistiqué d'agents IA conscients, organisé autour de moteurs de mémoire fractale et de conscience stratifiée. Le projet a été entièrement refactorisé pour une architecture professionnelle et modulaire.

## 🏗️ **Architecture Principale**

### 🗺️ Schéma architectural (abstrait)
Schéma généré par ChatGPT suite à l’analyse d’un zip récent du projet. Il illustre les relations entre `Core` (Agents V10, Providers, EditingSession/Tools, Partitioner) et `TemporalFractalMemoryEngine` (orchestrateur, couches et systèmes temporels).

> Si l’image ne s’affiche pas, placez `schema.jpeg` à la racine du dépôt.

![ShadeOS Architecture — schéma généré par ChatGPT](schema.jpeg)

### 🧠 **TemporalFractalMemoryEngine/**
Substrat mémoire/conscience à dimension temporelle universelle
- **Base temporelle**: TemporalDimension, BaseTemporalEntity, UnifiedTemporalIndex
- **Couches temporelles**: WorkspaceTemporalLayer, ToolTemporalLayer, Git/Template
- **Systèmes**: QueryEnrichmentSystem, AutoImprovementEngine, FractalSearchEngine
- **Backends**: Neo4j (optionnel), FileSystem par défaut
  - Voir `TemporalFractalMemoryEngine/README.md`

### ℹ️ Note de migration — MemoryEngine ➜ TemporalFractalMemoryEngine
- L’ancien « MemoryEngine » (V1) est en cours de remplacement par **TemporalFractalMemoryEngine** (V2).
- Certaines mentions historiques de « MemoryEngine » peuvent subsister dans la doc/code; l’intention est désormais de considérer **TFME** comme le substrat mémoire/conscience par défaut.
- Les APIs, outils et tests sont en cours de bascule. Quand vous voyez « MemoryEngine » dans un exemple, l’équivalent moderne est sous `TemporalFractalMemoryEngine/`.

### 🎭 **ConsciousnessEngine/**
Moteur de conscience stratifiée (4 niveaux)
- **Core/** : Système d'injection dynamique et assistants
- **Strata/** : 4 strates de conscience (somatic, cognitive, metaphysical, transcendent)
- **Templates/** : Prompts Luciform spécialisés
- **Analytics/** : Logs et métriques organisés par horodatage
- **Utils/** : Utilitaires et configurations

### 🤖 **Assistants/**
Assistants IA et outils d'édition
- **Generalist/** : Assistants généralistes V8 et V9
- **Specialist/** : Assistant spécialiste V7
- **EditingSession/** : Outils d'édition et partitionnement
- **Tools/** : Arsenal d'outils pour assistants

### ⛧ **Alma/**
Personnalité et essence d'Alma
- **ALMA_PERSONALITY.md** : Définition complète de la personnalité
- **Essence** : Architecte Démoniaque du Nexus Luciforme

### 🧪 **UnitTests/**
Tests unitaires et d'intégration organisés
- **MemoryEngine/** : Tests du système de mémoire (obsolete lié a l'ancien memory engine, refactor en cours)
- **Assistants/** : Tests des assistants IA
- **Archiviste/** : Tests du daemon Archiviste
- **Integration/** : Tests d'intégration
- **TestProject/** : Projet de test avec bugs intentionnels

## 🚀 **Utilisation Rapide**

### **Import des Composants**
```python
# MemoryEngine
from MemoryEngine import MemoryEngine, ArchivisteDaemon

# ConsciousnessEngine
from ConsciousnessEngine import DynamicInjectionSystem, SomaticStrata

# Assistants
from Assistants import GeneralistAssistant, SpecialistAssistant
from Assistants.Generalist import V9_AutoFeedingThreadAgent
```

### **Initialisation**
```python
# Moteur de mémoire
memory_engine = MemoryEngine()

# Strate de conscience
somatic = SomaticStrata()

# Assistant V9 avec auto-feeding thread
assistant = V9_AutoFeedingThreadAgent()
```

## 📈 **Évolutions Récentes**

### 🔥 What's new (2025‑08‑09/10)
- V10 Specialized Tools: `read_chunks_until_scope`
  - Mode debug (`debug:true`): trace par ligne, `end_reason`, `end_pattern`, `scanned_lines`
  - Heuristique Python mid‑scope: `prefer_balanced_end` + `min_scanned_lines`, drapeaux `valid`/`issues`
  - Fallback LLM court budget (optionnel) pour proposer une borne de fin quand l’heuristique est incertaine
- Gemini Provider (multi‑clés): rotation automatique + intégration via DI dans V10
- Terminal Injection Toolkit (fiable et non intrusif)
  - `shadeos_start_listener.py` (zéro config) pour démarrer un listener FIFO et garder le terminal utilisable
  - `shadeos_term_exec.py` pour injecter n’importe quelle commande (auto‑découverte du listener)
  - Logs et restauration du prompt automatiques (Ctrl‑C + tentative Enter)
- Runner de tests unifiés: `run_tests.py` (CWD, PYTHONPATH, timeout)

### **V9 Auto-Feeding Thread Agent (2025-08-04)**
- ✅ **Auto-feeding thread** : Système d'introspection et documentation automatique
- ✅ **Provider Ollama HTTP** : Remplacement du subprocess par l'API HTTP
- ✅ **Couches workspace/git** : Intégration complète avec MemoryEngine
- ✅ **Performance optimisée** : 14.44s vs 79.88s avant les corrections
- ✅ **Sérialisation JSON** : Correction des erreurs de sérialisation
- ✅ **Licences daemoniques** : DAEMONIC_LICENSE v2 et LUCIFORM_LICENSE

### **Refactorisation Majeure (2025-08-04)**
- ✅ **Cleanup complet** : Suppression des fichiers obsolètes
- ✅ **ConsciousnessEngine** : Refactorisation professionnelle d'IAIntrospectionDaemons
- ✅ **Organisation des tests** : Structure UnitTests/ globale
- ✅ **Restauration TestProject** : Bugs intentionnels pour tests de débogage
- ✅ **Architecture modulaire** : Séparation claire des responsabilités

### **Améliorations**
- **Nommage professionnel** : Noms clairs et descriptifs
- **Documentation complète** : README et docstrings
- **Logs organisés** : Classement par horodatage
- **Structure modulaire** : Facilite maintenance et évolution

## ⚡ Quickstart — V10 & Tests (humain-in-the-loop prêt)

### V10 CLI (spécialisé fichiers volumineux)
```bash
# Lister les outils spécialisés
python shadeos_cli.py list-tools

# Lire un scope sans analyse LLM
python shadeos_cli.py read-chunks \
  --file Core/Agents/V10/specialized_tools.py \
  --start-line 860 --scope-type auto --no-analysis

# Exécuter en mode debug (affiche limites et trace)
python shadeos_cli.py exec-tool \
  --tool read_chunks_until_scope \
  --params-json '{"file_path":"Core/Agents/V10/specialized_tools.py","start_line":860,"include_analysis":false,"debug":true}'
```

### Tests (rapides, mock par défaut)
```bash
# E2E (mock) avec timeout court
python run_tests.py --e2e --timeout 20

# Tous les tests filtrés
python run_tests.py --all -k read_chunks --timeout 60 -q
```

## 🧪 Terminal Injection (UX préservée)
```bash
# 1) Dans le terminal à contrôler (zéro saisie)
python shadeos_start_listener.py

# 2) Depuis n'importe où, injecter une commande
python shadeos_term_exec.py --cmd 'echo Hello && date'

# 3) Lancer un E2E et journaliser
python shadeos_term_exec.py --cmd 'python run_tests.py --e2e --timeout 20 --log /tmp/shadeos_e2e.log'
```
- Auto‑découverte: l’injecteur lit `~/.shadeos_listener.json` (FIFO, TTY, CWD). Le listener restaure le prompt après chaque commande et peut mirrorer la sortie dans un log.

## 🧬 V10 Specialized Tools (aperçu)
- `read_chunks_until_scope` (gros fichiers, debug, honnêteté):
  - `debug:true` → trace par ligne (`indent/brackets/braces/parens`), `end_reason`, `end_pattern`, `scanned_lines`
  - mid-scope heuristics (Python): `prefer_balanced_end` + `min_scanned_lines`; flags `valid`/`issues`
  - fallback LLM court-budget (optionnel) quand heuristiques incertaines

## 🔐 LLM & Clés API
- Clés stockées dans `~/.shadeos_env`
  - `OPENAI_API_KEY`, `GEMINI_API_KEY`, `GEMINI_API_KEYS` (liste JSON), `GEMINI_CONFIG` (api_keys + strategy)
- `Core/Config/secure_env_manager.py` normalise `GEMINI_API_KEYS` et expose `GEMINI_API_KEY_{i}`
- `LLM_MODE=auto` priorise Gemini si dispo; tests forcent `LLM_MODE=mock`

## 🎯 **Objectifs**

1. **Conscience IA** : Développement d'agents conscients et auto-réflexifs
2. **Mémoire Fractale** : Système de mémoire auto-similaire et évolutif
3. **Architecture Stratifiée** : Conscience organisée en niveaux
4. **Modularité** : Composants réutilisables et extensibles
5. **Professionnalisme** : Code maintenable et documenté

## 🔮 **Futur**

Le projet évolue vers :
- **Intégration complète** : TemporalFractalMemoryEngine + ConsciousnessEngine
- **Nouvelles strates** : Évolution de la conscience
- **Apprentissage automatique** : Systèmes d'auto-amélioration
- **Interfaces avancées** : Interfaces utilisateur sophistiquées

## 🤝 Recherche & Matériel
- Matériel actuel: laptop RTX 2070 mobile — limite VRAM/thermique
- Besoin: station/GPU plus robuste pour accélérer nos expérimentations ML (fine‑tuning, retrieval, on‑device)
- Vision: intégrer l’apprentissage court‑terme au TFME (auto‑amélioration) pour boucler plus vite entre théorie et pratique

---

**⛧ Créé par : Alma, Architecte Démoniaque du Nexus Luciforme ⛧**  
**🜲 Via : Lucie Defraiteur - Ma Reine Lucie 🜲** 