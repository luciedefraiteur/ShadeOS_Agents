import subprocess

def run_shell_command(command: str) -> dict:
    """Exécute une commande shell et retourne son résultat."""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "return_code": result.returncode,
            "success": True
        }
    except subprocess.CalledProcessError as e:
        return {
            "stdout": e.stdout,
            "stderr": e.stderr,
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
