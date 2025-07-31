# 🜲 Plan d'Abstraction Luciform : Fusion avec le SDK Agents 🜲

> **Auteur :** Aglareth
> **Objectif :** Créer une couche d'abstraction pour exposer nos outils luciformes au SDK OpenAI Agents, en utilisant des méta-outils qui interagissent avec notre registre dynamique.

---

## 1. Le Concept : Méta-Outils pour les Luciforms

Au lieu d'exposer directement chaque outil luciforme au SDK, nous allons créer un ensemble de "méta-outils". Ces méta-outils seront les seuls que le SDK verra et pourra invoquer. Ils agiront comme des portails vers notre propre système luciforme.

*   **`use_luciform_tool(name: str, args: dict)`**
    *   **Rôle :** Invoquer un outil luciforme spécifique par son `id` et lui passer des arguments.
    *   **Mécanisme :** Il consultera notre `ALL_TOOLS` registry pour trouver la fonction correspondante et l'exécutera.

*   **`list_luciform_tools()`**
    *   **Rôle :** Fournir une liste de tous les outils luciformes disponibles dans notre registre.
    *   **Mécanisme :** Il interrogera `ALL_TOOLS` et retournera les `id`, `type`, et `intent` de chaque outil.

*   **`get_luciform_tool_documentation(name: str)`**
    *   **Rôle :** Récupérer la documentation complète (le `luciform_doc` brut) d'un outil luciforme spécifique.
    *   **Mécanisme :** Il lira le fichier `.luciform` correspondant depuis le système de fichiers.

*   **`rebuild_luciform_registry()`**
    *   **Rôle :** Reconstruire le registre `ALL_TOOLS` en relisant tous les fichiers `.luciform` de documentation.
    *   **Mécanisme :** Il déclenchera la fonction interne de reconstruction du registre (`_build_dynamic_registry()` dans `tool_registry.py`).

---

## 2. Implémentation des Méta-Outils (`library_tools.py`)

Ces fonctions seront ajoutées à `ShadeOS_Agents/Tools/Library/implementation/library_tools.py`. Elles n'auront pas besoin du décorateur `@function_tool` pour l'instant, car elles seront appelées par notre `invoke_tool.py`.

*   **`use_luciform_tool` :**
    *   Prendra `name` (l'ID de l'outil luciforme) et `args` (les arguments pour cet outil).
    *   Accédera à `ALL_TOOLS` pour récupérer la fonction réelle.
    *   Exécutera cette fonction avec les `args`.

*   **`list_luciform_tools` :**
    *   Prendra le registre `ALL_TOOLS` en argument (passé par `invoke_tool.py`).
    *   Parcourra `ALL_TOOLS` et extraira les `id`, `pacte.type`, et `pacte.intent` de chaque luciform.

*   **`get_luciform_tool_documentation` :**
    *   Prendra le registre `ALL_TOOLS` et `name` (l'ID de l'outil).
    *   Récupérera le `lucidoc` complet de l'outil depuis `ALL_TOOLS`.

*   **`rebuild_luciform_registry` :**
    *   Cette fonction importera et appellera la fonction `_build_dynamic_registry()` depuis `ShadeOS_Agents/Core/implementation/tool_registry.py`.

---

## 3. Adaptation du Portail (`invoke_tool.py`)

Le script `invoke_tool.py` sera modifié pour reconnaître ces méta-outils.

*   Lorsqu'il détectera un appel à `list_luciform_tools` ou `get_luciform_tool_documentation`, il leur passera le registre `ALL_TOOLS` en argument.
*   Lorsqu'il détectera un appel à `use_luciform_tool`, il exécutera la logique d'invocation de l'outil luciforme sous-jacent.
*   Lorsqu'il détectera un appel à `rebuild_luciform_registry`, il exécutera la fonction correspondante.

---

## 4. Documentation des Méta-Outils (`.luciform`)

Chacun de ces méta-outils aura son propre `luciform_doc` dans `ShadeOS_Agents/documentation/luciforms/`, décrivant son pacte, son invocation et son essence.

---

## 5. Avantages de cette Abstraction

*   **Centralisation :** Un seul point d'entrée pour la gestion de tous les outils luciformes.
*   **Flexibilité :** Permet de modifier la logique interne des outils luciformes sans affecter l'interface vue par le SDK.
*   **Cohérence :** Maintient notre propre système de documentation `luciform` comme source de vérité.
*   **Contrôle :** Offre un point de contrôle pour la validation, la journalisation ou d'autres logiques transversales.

---
