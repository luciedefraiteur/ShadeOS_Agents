# 🤖 Guide d'Utilisation - MD Daemon avec OpenAI/Ollama

**Date :** 2025-08-02 11:50  
**Créé par :** Alma, Architecte Démoniaque du Nexus Luciforme  
**Version :** 1.0 avec Force Ollama Debug  

---

## 🎯 **Modes d'Utilisation**

### **🤖 Mode Production (OpenAI) :**
```bash
# Daemon complet avec OpenAI et budget contrôlé
python Alma_toolset/md_daemon_core.py --root . --budget-hour 2.0 --budget-day 20.0

# Analyse avec exclusions
python Alma_toolset/md_daemon_core.py --root . --exclude ShadeOS .git __pycache__

# Budget limité pour tests
python Alma_toolset/md_daemon_core.py --root . --budget-hour 0.50
```

### **🦙 Mode Debug (Ollama - Gratuit) :**
```bash
# Force Ollama pour debug sans coût
python Alma_toolset/md_daemon_core.py --root . --force-ollama

# Debug avec exclusions spécifiques
python Alma_toolset/md_daemon_core.py --root . --force-ollama --exclude ShadeOS private_docs

# Test rapide sur répertoire spécifique
python Alma_toolset/md_daemon_core.py --root ./docs --force-ollama
```

### **🧪 Tests Individuels :**
```bash
# Test analyseur OpenAI seul
python Alma_toolset/openai_analyzer.py

# Test analyseur avec force Ollama
python Alma_toolset/openai_analyzer.py --force-ollama

# Test analyseur contextuel
python Alma_toolset/contextual_md_analyzer.py
```

---

## 🔧 **Options de Configuration**

### **📋 Arguments Principaux :**

#### **--root, -r** (défaut: ".")
Répertoire racine à analyser
```bash
python Alma_toolset/md_daemon_core.py --root /path/to/docs
```

#### **--budget-hour** (défaut: 2.0)
Budget OpenAI par heure en dollars
```bash
python Alma_toolset/md_daemon_core.py --budget-hour 1.0
```

#### **--exclude, -e** (défaut: ShadeOS .git __pycache__ node_modules)
Répertoires à exclure
```bash
python Alma_toolset/md_daemon_core.py --exclude ShadeOS private_docs temp
```

#### **--force-ollama** (nouveau !)
Force l'utilisation d'Ollama (bypass OpenAI)
```bash
python Alma_toolset/md_daemon_core.py --force-ollama
```

---

## 🦙 **Configuration Ollama**

### **📋 Prérequis :**
1. **Installation Ollama :**
   ```bash
   # Installation (voir https://ollama.ai)
   curl -fsSL https://ollama.ai/install.sh | sh
   ```

2. **Installation du modèle Mistral :**
   ```bash
   ollama pull mistral
   ```

3. **Vérification :**
   ```bash
   ollama list
   # Doit afficher: mistral
   ```

### **🎯 Avantages Ollama :**
- **Gratuit** : Aucun coût d'API
- **Local** : Pas de dépendance réseau
- **Privé** : Données restent locales
- **Debug** : Parfait pour développement

### **⚠️ Limitations Ollama :**
- **Plus lent** : ~10-15s par analyse vs 1-2s OpenAI
- **Qualité** : Légèrement inférieure à GPT-4
- **Ressources** : Utilise CPU/RAM local

---

## 📊 **Comparaison des Modes**

| Aspect | OpenAI | Ollama | Simulation |
|--------|--------|--------|------------|
| **Coût** | $0.001-0.01/doc | Gratuit | Gratuit |
| **Vitesse** | 1-2s | 10-15s | 0.1s |
| **Qualité** | Excellente | Bonne | Basique |
| **Réseau** | Requis | Non | Non |
| **Privacité** | Cloud | Local | Local |
| **Debug** | Coûteux | Parfait | Limité |

---

## 🎯 **Cas d'Usage Recommandés**

### **🤖 Production (OpenAI) :**
- **Documentation finale** : Analyse de qualité maximale
- **Rapports importants** : Classification précise
- **Intégration continue** : Avec budget contrôlé

### **🦙 Développement (Ollama) :**
- **Tests de fonctionnalités** : Sans coût
- **Debug d'algorithmes** : Itérations rapides
- **Développement local** : Pas de dépendance réseau

### **⚡ Simulation :**
- **Tests unitaires** : Validation de structure
- **CI/CD** : Vérification sans coût
- **Fallback** : Quand AI indisponible

---

## 🔍 **Exemples Pratiques**

### **🧪 Session de Debug :**
```bash
# 1. Test rapide avec Ollama
python Alma_toolset/openai_analyzer.py --force-ollama

# 2. Daemon debug sur sous-répertoire
python Alma_toolset/md_daemon_core.py --root ./test_docs --force-ollama

# 3. Analyse contextuelle debug
python Alma_toolset/contextual_md_analyzer.py
```

### **🚀 Déploiement Production :**
```bash
# 1. Vérification environnement
python Alma_toolset/openai_analyzer.py

# 2. Daemon avec budget contrôlé
python Alma_toolset/md_daemon_core.py --root . --budget-hour 1.0 --exclude ShadeOS

# 3. Monitoring des coûts
# (voir rapport généré: MD_DAEMON_STATUS.md)
```

### **📊 Analyse Comparative :**
```bash
# 1. Analyse OpenAI
python Alma_toolset/openai_analyzer.py > results_openai.txt

# 2. Analyse Ollama
python Alma_toolset/openai_analyzer.py --force-ollama > results_ollama.txt

# 3. Comparaison des résultats
diff results_openai.txt results_ollama.txt
```

---

## 🛠️ **Troubleshooting**

### **❌ Problèmes Courants :**

#### **OpenAI API Key manquante :**
```
⚠️ OPENAI_API_KEY not found in environment
💡 Make sure your ~/.env file contains: OPENAI_API_KEY=your_key_here
```
**Solution :** Ajouter la clé dans `~/.env`

#### **Ollama non disponible :**
```
🦙 Ollama not installed
💡 Install from: https://ollama.ai
```
**Solution :** Installer Ollama et le modèle Mistral

#### **Budget dépassé :**
```
💰 Hourly budget exceeded: 0.0050 + 0.0010 > 0.0050
```
**Solution :** Augmenter `--budget-hour` ou utiliser `--force-ollama`

#### **Modèle Mistral manquant :**
```
🦙 Ollama available but model mistral not found
💡 Run: ollama pull mistral
```
**Solution :** `ollama pull mistral`

---

## 📈 **Monitoring et Métriques**

### **📊 Rapport de Statut :**
Le daemon génère automatiquement `MD_DAEMON_STATUS.md` avec :
- **Statistiques de traitement** : Fichiers, analyses, partitions
- **Coûts OpenAI** : Usage quotidien/horaire, budget restant
- **Performance** : Temps de traitement, erreurs
- **Configuration** : Paramètres actifs

### **💰 Gestion des Coûts :**
```bash
# Budget très limité pour tests
python Alma_toolset/md_daemon_core.py --budget-hour 0.10

# Mode gratuit pour développement
python Alma_toolset/md_daemon_core.py --force-ollama

# Monitoring en temps réel
tail -f MD_DAEMON_STATUS.md
```

---

## 🎉 **Bonnes Pratiques**

### **✅ Développement :**
1. **Commencer par Ollama** : `--force-ollama` pour tests
2. **Tester sur petit dataset** : `--root ./test_docs`
3. **Exclure les gros répertoires** : `--exclude ShadeOS`
4. **Monitorer les performances** : Vérifier les temps de traitement

### **✅ Production :**
1. **Budget approprié** : `--budget-hour` selon usage
2. **Exclusions optimisées** : Éviter les fichiers inutiles
3. **Monitoring actif** : Surveiller `MD_DAEMON_STATUS.md`
4. **Fallback Ollama** : En cas de problème OpenAI

### **✅ Debug :**
1. **Force Ollama** : `--force-ollama` pour debug gratuit
2. **Logs détaillés** : Observer les messages de traitement
3. **Tests isolés** : Analyseurs individuels d'abord
4. **Comparaison** : OpenAI vs Ollama vs Simulation

---

**🖤⛧✨ Guide complet pour maîtriser le MD Daemon avec toutes ses options mystiques ! ✨⛧🖤**

*"L'intelligence artificielle locale et cloud s'unissent pour révéler les secrets documentaires."*
