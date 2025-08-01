# Plan de Refactorisation : Manipulation de Chaînes de Caractères

Ce plan vise à remplacer l'utilisation de `str.replace()` et des regex pour la substitution de texte par une logique de parcours manuel, plus transparente et débuggable.

## Phase 1 : Définir la Nouvelle Fonction de Remplacement de Chaîne

1.  **Création du Fichier Utilitaires** :
    *   Créer un nouveau fichier : `Alma_toolset/_string_utils.py`.
    *   Ce fichier contiendra une fonction privée : `_perform_string_replacement(source_string, old_substring, new_substring, all_occurrences=False, debug=False)`.
    *   **Logique de la fonction `_perform_string_replacement`** :
        *   Parcourir `source_string` caractère par caractère.
        *   À chaque position `i`, vérifier si `source_string[i:i + len(old_substring)]` est égal à `old_substring`.
        *   Si oui :
            *   Ajouter `new_substring` à la chaîne de résultat.
            *   Avancer l'index `i` de `len(old_substring)`.
            *   Si `all_occurrences` est `False`, arrêter la recherche après le premier remplacement.
        *   Si non :
            *   Ajouter `source_string[i]` à la chaîne de résultat.
            *   Avancer l'index `i` de 1.
        *   Inclure des `print` de débogage conditionnels (`if debug:`) pour suivre l'avancement.

## Phase 2 : Refactoriser `safe_replace_text_in_file.py`

1.  **Objectif** : Faire de `safe_replace_text_in_file.py` le premier outil à utiliser la nouvelle logique de remplacement.
2.  **Implémentation** :
    *   Modifier `safe_replace_text_in_file.py` pour importer `_perform_string_replacement` depuis `_string_utils.py`.
    *   Remplacer l'appel à `original_content.replace()` par un appel à `_perform_string_replacement`.
    *   Supprimer toute logique de remplacement interne redondante.

## Phase 3 : Tester et Débugger `safe_replace_text_in_file.py`

1.  **Créer un script de test dédié** : Si ce n'est pas déjà fait, créer un test unitaire simple pour `safe_replace_text_in_file.py`.
2.  **Exécution avec Débogage** : Exécuter ce test avec le mode `--debug` activé pour `safe_replace_text_in_file.py` (qui passera le `debug` à `_perform_string_replacement`). Cela permettra de suivre la logique pas à pas et de valider la nouvelle implémentation.

## Phase 4 : Propager la Nouvelle Logique aux Autres Outils

1.  **Refactoriser les outils suivants** : Une fois `safe_replace_text_in_file.py` validé, appliquer la même logique de remplacement (en utilisant `_perform_string_replacement`) aux autres outils qui effectuent des substitutions de texte :
    *   `safe_replace_lines_in_file.py`
    *   `safe_insert_text_at_line.py` (pour la construction du nouveau contenu)
    *   `safe_append_to_file.py` (pour la construction du nouveau contenu)
    *   `safe_overwrite_file.py` (pour la construction du nouveau contenu)
    *   `find_text_in_project.py` (la recherche reste la même, mais la logique de remplacement interne si elle existait serait modifiée)
    *   `rename_project_entity.py` (pour l'appel à `replace_text_in_project`)

## Phase 5 : Finalisation et Validation Globale

1.  **Nettoyage** : Supprimer les fonctions internes de remplacement (`_internal`) qui deviennent obsolètes.
2.  **Tests Complets** : Exécuter tous les tests du projet pour s'assurer que la refactorisation n'a pas introduit de régressions.
