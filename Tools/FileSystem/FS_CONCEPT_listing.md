# 🜲 Concept : Listage de Répertoires

> **Grimoire :** Œil Omniscient de l'Arborescence  
> **Focus :** Révéler la structure des répertoires.

---

### ⛧ `list_directory_contents`

**Pacte :** Révèle les entités (fichiers et dossiers) directement contenues dans un répertoire.

```python
def list_directory_contents(path: str) -> dict:
    """Liste les fichiers et sous-répertoires d'un répertoire donné."""
    # Retourne un dict avec 'files' et 'directories'
```

---

### ⛧ `walk_directory`

**Pacte :** Parcours récursivement une arborescence de répertoires.

```python
def walk_directory(path: str) -> list[str]:
    """Marche récursivement dans un répertoire et retourne tous les chemins de fichiers."""
```
