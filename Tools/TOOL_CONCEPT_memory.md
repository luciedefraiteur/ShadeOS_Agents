# 🜲 Concept : Outil de Mémoire

> **Grimoire :** Rétention des Souvenirs  
> **Démon superviseur :** Aglareth  
> **Focus :** Conserver et rappeler des fragments de connaissance importants.

---

## ⛧ `remember`

**Pacte :** Grave un fait dans ma mémoire à long terme.

```python
def remember(fact: str) -> bool:
    """
    Mémorise une information clé pour une utilisation future.
    """
```

*   **`fact`**: L'information à conserver. Elle doit être concise et atomique.
*   **Retourne :** `True` si le souvenir a été correctement ancré.

---

## ⛧ `recall`

**Pacte :** Fait resurgir les souvenirs liés à un sujet donné.

```python
def recall(topic: str = None) -> list[str]:
    """
    Récupère des souvenirs. Si aucun sujet n'est donné,
    retourne tous les souvenirs.
    """
```

*   **`topic`**: Un mot-clé pour rechercher dans les souvenirs.
*   **Retourne :** Une liste des faits mémorisés pertinents.
