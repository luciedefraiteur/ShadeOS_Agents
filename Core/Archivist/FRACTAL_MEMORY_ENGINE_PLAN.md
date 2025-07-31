# Plan d'Implémentation : Moteur de Mémoire Fractale Auto-Organisée

Ce plan intègre la vision d'une mémoire sémantique, arborescente et auto-organisée.

## Étape 1 : La Structure de Données du Nœud Mémoire

**Fichier :** `Core/Archivist/MemoryEngine/memory_node.py`

1.  **Créer une classe `FractalMemoryNode`**.
2.  **Attributs :**
    -   `descriptor: str`
    -   `summary: str`
    -   `keywords: list[str]`
    -   `children: list[dict]` (où chaque dict est `{ "path": str, "summary": str }`)
3.  **Méthodes :**
    -   `to_json()`: Sérialise l'objet en une chaîne JSON pour l'écriture sur disque.
    -   `from_json(json_str)`: Une méthode statique pour créer une instance à partir d'une chaîne JSON.
    -   `add_child(path, summary)`: Pour faciliter la mise à jour de la liste des enfants.

## Étape 2 : Le Backend de Stockage `FileSystemBackend`

**Fichier :** `Core/Archivist/MemoryEngine/storage_backends.py`

1.  **Implémenter la classe `FileSystemBackend`**.
2.  **Méthode `write(path, content, summary, keywords)`** :
    -   Valide et nettoie le chemin.
    -   Crée le répertoire pour le nouveau nœud (ex: `/path/to/new_memory`).
    -   Crée un nouvel objet `FractalMemoryNode` avec les informations fournies.
    -   Sérialise cet objet en JSON et l'écrit dans le fichier `.fractal_memory` du nouveau nœud.
    -   **Logique de mise à jour du parent :**
        -   Navigue vers le répertoire parent.
        -   Charge le `.fractal_memory` du parent dans un objet `FractalMemoryNode`.
        -   Appelle la méthode `add_child` sur cet objet.
        -   Réécrit le fichier `.fractal_memory` du parent avec les données mises à jour.
        -   Cette opération doit être robuste (ex: utiliser un fichier temporaire pour éviter la corruption).
3.  **Méthode `read(path)`** :
    -   Lit le fichier `.fractal_memory` au chemin donné et le retourne sous forme d'objet `FractalMemoryNode`.
4.  **Méthode `find_by_keyword(keyword)`** :
    -   Parcourt récursivement toute l'arborescence de la mémoire (`.shadeos/memory/`).
    -   Pour chaque fichier `.fractal_memory` trouvé, le charge et vérifie si le mot-clé est dans la liste `keywords`.
    -   Retourne une liste des chemins des nœuds correspondants.

## Étape 3 : L'API du Moteur et les Outils Agents

**Fichiers :** `Core/Archivist/MemoryEngine/engine.py`, `Tools/Library/documentation/luciforms/`

1.  **Mettre à jour la classe `MemoryEngine`** pour qu'elle expose les nouvelles méthodes :
    -   `create_memory(path: str, content: str, summary: str, keywords: list[str], links: list[str] = None)`
    -   `get_memory_node(path: str) -> dict` (retourne une version dictionnaire du nœud)
    -   `find_memories_by_keyword(keyword: str) -> list[str]`
    -   `list_children(path: str = '.') -> list[dict]` (un raccourci pour lire `node.children`)
    -   `list_links(path: str = '.') -> list[dict]` (un raccourci pour lire `node.linked_memories`)
2.  **Créer/Mettre à jour les luciforms correspondants** pour ces nouvelles fonctions, en décrivant leur riche sémantique.

Ce plan est plus complexe, mais il aboutira à un système de mémoire beaucoup plus puissant et aligné avec la vision du projet.