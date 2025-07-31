# 🜲 Concept : Modification de Fichiers

> **Grimoire :** Scalpel Alchimique  
> **Focus :** Altérer avec précision le contenu existant d'un fichier.

---

### ⛧ `replace_text_in_file`

**Pacte :** Transmute une séquence de symboles en une autre.

```python
def replace_text_in_file(path: str, old_text: str, new_text: str, all_occurrences: bool = False) -> bool:
    """Remplace la première ou toutes les occurrences d'un texte dans un fichier."""
```

---

### ⛧ `replace_lines_in_file`

**Pacte :** Remplace un bloc de lignes par un nouveau contenu.

```python
def replace_lines_in_file(path: str, start_line: int, end_line: int, new_lines: list[str]) -> bool:
    """Remplace une plage de lignes par de nouvelles lignes."""
```

---

### ⛧ `insert_text_at_line`

**Pacte :** Insère du texte à une ligne spécifique, décalant le reste.

```python
def insert_text_at_line(path: str, line_number: int, text_to_insert: str) -> bool:
    """Insère un bloc de texte à un numéro de ligne donné."""
```
