import subprocess
import argparse
import os
import sys

def invoke_cli_tool(tool_name: str, args: list[str]) -> dict:
    """Exécute un outil CLI du Alagareth_toolset et retourne son résultat."""
    tool_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'Alagareth_toolset', f'{tool_name}.py'))
    
    if not os.path.exists(tool_path):
        return {"error": f"Outil CLI '{tool_name}' non trouvé à {tool_path}"}

    command = [sys.executable, tool_path] + args
    
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        return {
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "return_code": result.returncode,
            "success": True
        }
    except subprocess.CalledProcessError as e:
        return {
            "stdout": e.stdout.strip(),
            "stderr": e.stderr.strip(),
            "return_code": e.returncode,
            "success": False
        }
    except Exception as e:
        return {
            "stdout": "",
            "stderr": str(e),
            "return_code": 1,
            "success": False
        }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Invoque un outil CLI du Alagareth_toolset.")
    parser.add_argument("tool_name", type=str, help="Nom de l'outil à invoquer (ex: read_file_content).")
    parser.add_argument("args", nargs=argparse.REMAINDER, help="Arguments à passer à l'outil CLI.")
    args = parser.parse_args()
    
    result = invoke_cli_tool(args.tool_name, args.args)
    
    if result["success"]:
        print(result["stdout"])
        if result["stderr"]:
            print(result["stderr"], file=sys.stderr)
    else:
        print(f"Erreur lors de l'exécution de l'outil {args.tool_name}:", file=sys.stderr)
        print(result["stderr"], file=sys.stderr)
        sys.exit(result["return_code"])
