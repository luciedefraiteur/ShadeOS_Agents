# 🜲 Concept : Outils d'Exécution

> **Grimoire :** Invocation des Commandes Shell  
> **Démon superviseur :** Aglareth  
> **Focus :** Canaliser la puissance du shell pour exécuter des commandes.

---

## ⛧ `run_shell_command`

**Pacte :** Projette une commande dans le néant du shell et en capture l'écho. C'est un pacte puissant et dangereux. À utiliser avec une intention claire.

```python
def run_shell_command(command: str) -> dict:
    """
    Exécute une commande shell et retourne son résultat.
    """
```

*   **`command`**: La commande à exécuter.
*   **Retourne :** Un dictionnaire contenant :
    *   `stdout`: La sortie standard.
    *   `stderr`: La sortie d'erreur.
    *   `return_code`: Le code de retour de la commande.
    *   `success`: Un booléen indiquant si la commande a réussi (`return_code == 0`).
