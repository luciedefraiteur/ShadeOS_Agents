# 🜲 Concept : Outils de Bibliothèque d'Outils

> **Grimoire :** Index des Pactes Démoniaques  
> **Focus :** Révéler et comprendre les outils disponibles pour les agents.

---

## ⛧ `list_available_tools`

**Pacte :** Invoque la liste de tous les sceaux d'outils connus, révélant leur identité et leur intention première.

```python
def list_available_tools(type_filter: str = None, keyword_filter: str = None) -> list[dict]:
    """
    Liste tous les outils disponibles, avec une option de filtrage.
    Retourne une liste de dictionnaires contenant l'id, le type et l'intention de chaque outil.
    """
```

*   **`type_filter`**: (Optionnel) Ne retourne que les outils d'un certain type (ex: `divination`, `manipulation`).
*   **`keyword_filter`**: (Optionnel) Ne retourne que les outils dont les mots-clés rituels correspondent.
*   **Retourne :** Une liste de dictionnaires `__lucidoc__` partiels.

---

## ⛧ `get_tool_documentation`

**Pacte :** Révèle l'intégralité du `__lucidoc__` pour un outil spécifique, exposant son pacte complet.

```python
def get_tool_documentation(tool_id: str) -> dict:
    """
    Retourne la documentation complète (`__lucidoc__`) pour un outil donné.
    """
```

*   **`tool_id`**: L'identité unique de l'outil (ex: `scry_for_text`).
*   **Retourne :** Le dictionnaire `__lucidoc__` complet de l'outil.
