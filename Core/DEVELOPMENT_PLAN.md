# Plan de Développement - Phase 1 (Pré-API) - Révisé v2

**Analyse :** Sur la base des clarifications, l'utilisation d'un parseur XML standard est rejetée pour préserver la flexibilité future des luciforms (ex: injections de code). Le parseur maison doit donc être conservé. Cependant, l'implémentation actuelle reste trop complexe : le parseur génère un arbre générique qui nécessite une fonction de "reconstruction" compliquée dans le registre.

**Objectif :** Conserver un parseur maison tout en simplifiant radicalement le code en le rendant plus intelligent.

## Étape 1 : Refactoriser le Parseur de Luciforms pour une Sortie Sémantique

**Fichier :** `Core/implementation/luciform_parser.py`

**Objectif :** Modifier le parseur maison pour qu'il ne produise plus un arbre générique, mais directement un dictionnaire Python propre qui représente la structure sémantique du luciform.

-   **Action :** Réécrire la logique de `parse_luciform` pour qu'elle construise le dictionnaire final au fur et à mesure du parcours des balises.
-   **Exemple de sortie attendue :**
    ```python
    {
        "id": "read_file_content",
        "pacte": {
            "type": "reading",
            "intent": "Invoquer l'intégralité du contenu d'un fichier.",
            "level": "fondamental"
        },
        "invocation": { ... },
        "essence": { ... }
    }
    ```
-   **Bénéfice :** Le parseur devient la seule source de vérité pour l'interprétation des luciforms. La complexité est contenue en un seul endroit.

## Étape 2 : Simplifier Radicalement le Registre d'Outils

**Fichier :** `Core/implementation/tool_registry.py`

**Objectif :** Éliminer la logique de reconstruction redondante.

-   **Action :**
    1.  Supprimer complètement la fonction `_reconstruct_doc_from_tree`.
    2.  Modifier `_build_dynamic_registry` pour assigner directement le résultat du nouveau `parse_luciform` à la clé `lucidoc` de l'outil.
-   **Bénéfice :** Le code du registre devient trivial, lisible et robuste.

## Étape 3 : Adapter les Tests et Valider

**Fichiers :** `Core/implementation/test_parse_luciform.py`, `Core/implementation/test_tool_registry.py` (à créer)

**Objectif :** Assurer que la nouvelle implémentation est correcte et stable.

-   **Actions :**
    1.  Modifier `test_parse_luciform.py` pour qu'il vérifie la nouvelle structure de sortie (dictionnaire sémantique).
    2.  Créer `test_tool_registry.py` pour faire un test d'intégration : charger tous les outils et vérifier qu'un outil de référence est correctement et complètement chargé dans `ALL_TOOLS`.
-   **Bénéfice :** Confiance dans le cœur du système et protection contre les régressions.
