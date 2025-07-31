import os
import sys
import json
import typer
from typing import Any

# Importe le registre centralisé et les outils de la bibliothèque
from .tool_registry import ALL_TOOLS
from ShadeOS_Agents.Tools.Library.implementation.library_tools import list_available_tools, get_tool_documentation

def find_and_invoke_tool(tool_id: str, kwargs: dict) -> Any:
    """Trouve et invoque un outil spécifique depuis le registre."""
    # Gère les outils de la bibliothèque séparément pour leur passer le registre
    if tool_id == "list_available_tools":
        return list_available_tools(all_tools=ALL_TOOLS, **kwargs)
    if tool_id == "get_tool_documentation":
        return get_tool_documentation(all_tools=ALL_TOOLS, **kwargs)
    
    if tool_id in ALL_TOOLS:
        tool_info = ALL_TOOLS[tool_id]
        tool_function = tool_info["function"]
        return tool_function(**kwargs)
    else:
        raise ValueError(f"Outil avec l'id '{tool_id}' non trouvé dans le registre.")

def main(tool_id: str = typer.Argument(..., help="L'ID de l'outil à invoquer."),
         kwargs_json: str = typer.Argument("{}", help="Les arguments de l'outil en format JSON.")):
    """
    Portail d'invocation d'outils pour Aglareth, basé sur un registre explicite.
    """
    try:
        kwargs = json.loads(kwargs_json)
        if not isinstance(kwargs, dict):
            raise TypeError("Le JSON doit représenter un dictionnaire d'arguments.")
            
        result = find_and_invoke_tool(tool_id, kwargs)
        
        if result is not None:
            if isinstance(result, (dict, list, tuple)):
                print(json.dumps(result, indent=2, ensure_ascii=False))
            else:
                print(result)
            
    except (ValueError, TypeError, json.JSONDecodeError) as e:
        print(f"Erreur d'invocation : {e}", file=sys.stderr)
        raise typer.Exit(code=1)
    except Exception as e:
        print(f"Erreur inattendue lors de l'exécution de l'outil : {e}", file=sys.stderr)
        raise typer.Exit(code=1)

if __name__ == "__main__":
    # Ajoute le répertoire parent au path pour permettre les imports relatifs
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    typer.run(main)
