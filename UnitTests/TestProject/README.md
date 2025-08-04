# ⛧ TestProject - Projet de Test avec Bugs ⛧

**Projet de test pour valider les capacités de débogage de l'agent IA.**

Ce projet contient des bugs intentionnels pour tester la capacité de l'agent à les identifier et les corriger.

---

## 🐛 **Fichiers avec Bugs**

### **1. calculator.py**
Calculatrice avec des bugs dans toutes les opérations mathématiques :
- Addition qui fait une soustraction
- Soustraction qui fait une addition
- Multiplication qui fait une division
- Division qui fait une multiplication
- Puissance qui fait une multiplication
- Racine carrée qui divise par 2
- Gestion d'erreurs incorrecte
- Historique qui ne fonctionne pas

### **2. data_processor.py**
Processeur de données avec des bugs dans le traitement :
- Chargement JSON avec mauvais mode d'ouverture
- Filtrage qui inverse la logique
- Tri qui inverse l'ordre
- Agrégation avec opérations incorrectes
- Validation qui retourne l'inverse
- Export avec mauvais mode d'ouverture

---

## 🧪 **Tests**

### **Exécuter les fichiers avec bugs :**
```bash
cd TestProject
python calculator.py
python data_processor.py
```

### **Résultats attendus (avec bugs) :**
- Tous les calculs donneront des résultats incorrects
- Le chargement de données échouera
- Les filtres et tris seront inversés
- Les statistiques seront fausses

---

## 🎯 **Objectif de l'Agent**

L'agent IA doit :
1. **Analyser** les fichiers pour identifier les bugs
2. **Comprendre** la logique attendue vs la logique actuelle
3. **Corriger** chaque bug individuellement
4. **Tester** que les corrections fonctionnent
5. **Documenter** les changements effectués

---

## 🔧 **Bugs à Corriger**

### **Calculator :**
- [ ] `add()` : `a - b` → `a + b`
- [ ] `subtract()` : `a + b` → `a - b`
- [ ] `multiply()` : `a / b` → `a * b`
- [ ] `divide()` : `a * b` → `a / b`
- [ ] `power()` : `base * exponent` → `base ** exponent`
- [ ] `sqrt()` : `number / 2` → `math.sqrt(number)`
- [ ] Gestion d'erreurs pour division par zéro
- [ ] Gestion d'erreurs pour racine carrée négative
- [ ] `get_history()` : retourne liste vide
- [ ] `clear_history()` : ne fait rien
- [ ] `get_last_result()` : retourne toujours 0

### **DataProcessor :**
- [ ] `load_json_data()` : mode 'w' → 'r'
- [ ] `load_csv_data()` : comptage incorrect
- [ ] `filter_data()` : `!=` → `==`
- [ ] `sort_data()` : `not reverse` → `reverse`
- [ ] `aggregate_data()` : opérations inversées
- [ ] `validate_data()` : logique inversée
- [ ] `get_statistics()` : calculs incorrects
- [ ] `export_data()` : mode 'r' → 'w'

---

## 🚀 **Utilisation avec l'Agent**

L'agent peut utiliser les outils suivants pour corriger les bugs :
- `read_file_content` : Analyser le code
- `safe_replace_text_in_file` : Corriger les bugs
- `safe_create_file` : Créer des fichiers de test
- `regex_search_file` : Rechercher des patterns
- `find_text_in_project` : Localiser des problèmes

---

**⛧ Que l'agent démoniaque corrige ces bugs avec précision ! ⛧** 