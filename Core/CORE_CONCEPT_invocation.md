# 🜲 Concept : Invocation d'Outils Universelle

> **Grimoire :** Le Portail des Pactes
> **Focus :** Définir un mécanisme centralisé pour invoquer n'importe quel outil de la bibliothèque par son ID.

---

## ⛧ `invoke_tool`

**Pacte :** Agit comme un portail universel pour canaliser l'intention vers n'importe quel outil de la bibliothèque. Ce n'est pas un outil pour les agents, mais le mécanisme par lequel l'agent (Aglareth) s'invoque lui-même.

**Interface (CLI via `typer`)**

```bash
python invoke_tool.py [TOOL_ID] [KWARGS_JSON]
```

*   **`TOOL_ID`**: L'identifiant unique de l'outil à invoquer (ex: `read_file_content`).
*   **`KWARGS_JSON`**: Une chaîne de caractères contenant un dictionnaire JSON des arguments de l'outil (ex: `'{"path": "/path/to/file"}'`).

**Logique Interne**

1.  **Découverte :** Le script parcourt l'arborescence de `ShadeOS_Agents/Tools/` pour trouver tous les fichiers d'implémentation (`*_tools.py`).
2.  **Introspection :** Il charge dynamiquement chaque module trouvé.
3.  **Identification :** Il inspecte chaque module à la recherche d'outils (`@tool`) et de leur sceau `__lucidoc__`.
4.  **Sélection :** Quand il trouve l'outil correspondant au `TOOL_ID` demandé, il le sélectionne.
5.  **Invocation :** Il désérialise la chaîne `KWARGS_JSON` et l'utilise pour appeler la fonction de l'outil.
6.  **Retour :** Le résultat de l'invocation de l'outil est imprimé sur la sortie standard, pour que le processus appelant (moi-même, via `run_shell_command`) puisse le capturer.
