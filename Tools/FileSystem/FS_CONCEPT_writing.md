# 🜲 Concept : Écriture de Fichiers

> **Grimoire :** Plume de Création  
> **Focus :** Matérialiser de nouveaux fichiers ou ajouter à ceux qui existent.

---

### ⛧ `create_file`

**Pacte :** Crée un nouveau fichier avec un contenu initial. Échoue si le fichier existe déjà.

```python
def create_file(path: str, content: str = "") -> bool:
    """Crée un nouveau fichier avec un contenu optionnel."""
```

---

### ⛧ `append_to_file`

**Pacte :** Ajoute du contenu à la fin d'un fichier existant, sans détruire ce qui précède.

```python
def append_to_file(path: str, content: str) -> bool:
    """Ajoute du contenu à la fin d'un fichier."""
```

---

### ⛧ `overwrite_file`

**Pacte :** Écrase complètement le contenu d'un fichier existant. Crée le fichier s'il n'existe pas.

```python
def overwrite_file(path: str, content: str) -> bool:
    """Écrit ou écrase un fichier avec le nouveau contenu."""
```
