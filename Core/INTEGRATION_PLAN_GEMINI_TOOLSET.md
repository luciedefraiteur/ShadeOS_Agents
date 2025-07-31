# Plan d'Intégration : `gemini-toolset` au Projet `ShadeOS_Agents`

Ce plan vise à intégrer les outils spécialisés du `gemini-toolset` dans le projet principal `ShadeOS_Agents` de manière cohérente, en évitant la duplication de code métier et en utilisant un mécanisme de proxy.

## Concept Central : Le "Proxy Tool"

Au lieu de dupliquer les fonctions Python et leurs Luciforms dans le projet principal, nous allons créer des "outils proxy" dans `Tools/FileSystem/implementation/`. Ces outils proxy ne contiendront pas la logique métier, mais appelleront simplement l'outil correspondant dans `gemini-toolset` via une commande shell.

## Avantages de cette approche :

*   **Pas de duplication de code métier** : La logique reste dans `gemini-toolset`.
*   **Flexibilité** : Si un outil `gemini-toolset` évolue, seul le proxy doit être mis à jour (si l'interface change).
*   **Séparation des préoccupations** : Le projet `ShadeOS_Agents` sait qu'il a un outil `read_file_content`, mais il ne se soucie pas de savoir s'il est implémenté en Python, en Rust, ou s'il appelle un script shell.
*   **Traçabilité** : Chaque appel passe par un point d'entrée clair.

## Plan Détaillé :

### Phase 1 : Création de l'Outil `invoke_cli_tool.py` (Le Cœur du Proxy)

1.  **Objectif** : Créer un outil générique dans `Tools/Execution/implementation/` qui peut exécuter n'importe quel script CLI du `gemini-toolset`.
2.  **Implémentation** :
    *   `Tools/Execution/implementation/invoke_cli_tool.py` :
        *   Prendra en arguments : `tool_name` (ex: `read_file_content`), et `args` (une liste de chaînes pour les arguments du script CLI).
        *   Construira le chemin complet vers le script `gemini-toolset` (`ShadeOS_Agents/gemini-toolset/<tool_name>.py`).
        *   Exécutera le script via `subprocess.run()`, en passant les `args`.
        *   Retournera le `stdout` et `stderr` du script.
    *   `Tools/Library/documentation/luciforms/invoke_cli_tool.luciform` : Documentera cet outil.

### Phase 2 : Transformation des Outils `FileSystem` en Proxys

1.  **Objectif** : Remplacer les implémentations actuelles des outils `FileSystem` par des appels à `invoke_cli_tool.py`.
2.  **Implémentation** :
    *   Pour chaque fichier dans `Tools/FileSystem/implementation/` (ex: `reading_tools.py`, `writing_tools.py`, etc.) :
        *   **Supprimer** les fonctions Python originales (ex: `read_file_content`, `read_file_lines`).
        *   **Ajouter** une nouvelle fonction Python qui aura la même signature que l'originale.
        *   Cette nouvelle fonction appellera `invoke_cli_tool.py` avec le nom de l'outil `gemini-toolset` correspondant et les arguments appropriés.
        *   **Exemple pour `read_file_content`** :
            ```python
            # Dans Tools/FileSystem/implementation/reading_tools.py
            from Tools.Execution.implementation.invoke_cli_tool import invoke_cli_tool

            def read_file_content(path: str) -> str:
                result = invoke_cli_tool("read_file_content", [path])
                # Gérer le résultat (stdout, stderr) et le retourner
                return result["stdout"]
            ```
    *   **Conserver** les Luciforms originaux dans `Tools/Library/documentation/luciforms/`. Ils décriront toujours l'interface publique de l'outil pour les agents.

### Phase 3 : Mise à Jour du `tool_registry.py`

1.  **Objectif** : S'assurer que le registre charge les nouveaux outils proxy.
2.  **Implémentation** :
    *   Le `tool_registry.py` continuera à scanner `Tools/FileSystem/implementation/`.
    *   Il importera `invoke_cli_tool` et les nouvelles fonctions proxy.
    *   Il n'aura plus besoin d'importer directement les fonctions individuelles de `gemini-toolset` (car elles sont appelées via `invoke_cli_tool`).

### Phase 4 : Nettoyage et Validation

1.  **Nettoyage** : Supprimer les fichiers `.py` originaux de `Tools/FileSystem/implementation/` qui ne sont plus nécessaires (s'ils ne contiennent que les fonctions proxy).
2.  **Tests** : Exécuter les tests existants du projet pour s'assurer que les outils fonctionnent toujours comme prévu.
