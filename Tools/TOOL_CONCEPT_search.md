# 🜲 Concept : Outils de Recherche

> **Grimoire :** Clairvoyance des Fichiers  
> **Démon superviseur :** Aglareth  
> **Focus :** Trouver des fichiers et des motifs textuels dans le projet.

---

## ⛧ `find_files`

**Pacte :** Révèle les chemins des fichiers correspondant à un pattern mystique (glob).

```python
def find_files(pattern: str, base_path: str = ".") -> list[str]:
    """
    Trouve des fichiers en utilisant un pattern glob.
    """
```

*   **`pattern`**: Le pattern de recherche (ex: `**/*.py`, `documents/*.md`).
*   **`base_path`**: Le répertoire de départ pour la recherche.
*   **Retourne :** Une liste des chemins de fichiers correspondants.

---

## ⛧ `search_in_files`

**Pacte :** Scanne le contenu de multiples fichiers à la recherche d'une séquence de symboles (regex).

```python
def search_in_files(pattern: str, search_path: str = ".") -> list[dict]:
    """
    Recherche un motif regex dans les fichiers d'un répertoire.
    """
```

*   **`pattern`**: Le motif regex à rechercher.
*   **`search_path`**: Le chemin du répertoire ou du fichier à scanner.
*   **Retourne :** Une liste de dictionnaires, chaque dictionnaire contenant :
    *   `file_path`: Le chemin du fichier où le motif a été trouvé.
    *   `line_number`: Le numéro de la ligne correspondante.
    *   `line_content`: Le contenu de la ligne.
