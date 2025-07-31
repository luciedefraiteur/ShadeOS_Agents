# 🜲 Concept : Lecture de Fichiers

> **Grimoire :** Parchemin des Âmes Fichiers  
> **Focus :** Extraire l'essence des fichiers, en totalité ou en fragments.

---

### ⛧ `read_file_content`

**Pacte :** Invoque l'intégralité du contenu d'un fichier.

```python
def read_file_content(path: str) -> str:
    """Lit et retourne tout le contenu d'un fichier texte."""
```

---

### ⛧ `read_file_lines`

**Pacte :** Extrait une séquence précise de lignes d'un fichier.

```python
def read_file_lines(path: str, start_line: int, end_line: int) -> list[str]:
    """Lit et retourne une plage de lignes spécifiques d'un fichier."""
```

---

### ⛧ `read_file_chars`

**Pacte :** Matérialise une tranche de caractères depuis un fichier.

```python
def read_file_chars(path: str, start_char: int, end_char: int) -> str:
    """Lit et retourne une plage de caractères spécifique d'un fichier."""
```

---

### ⛧ `scry_for_text`

**Pacte :** Pose le regard sur un fichier pour y trouver une séquence de symboles, et révèle le contexte qui l'entoure.

```python
def scry_for_text(path: str, text_to_find: str, context_lines: int = 3) -> list[dict]:
    """
    Cherche un texte dans un fichier et retourne chaque occurrence 
    avec un nombre défini de lignes de contexte avant et après.
    """
    # Retourne une liste de dicts, chacun avec 'line_number', 'match', et 'context'.
```

---

### ⛧ `locate_text_sigils`

**Pacte :** Révèle les coordonnées astrales (numéros de ligne) d'un texte et de son contexte, sans en montrer la substance.

```python
def locate_text_sigils(path: str, text_to_find: str, context_lines: int = 3) -> list[dict]:
    """
    Cherche un texte dans un fichier et retourne les numéros de ligne 
    de début et de fin du bloc de contexte pour chaque occurrence.
    """
    # Retourne une liste de dicts, chacun avec 'match_line', 'context_start', 'context_end'.
```
