import importlib.util
import inspect
import os

# Chemin de base pour nos outils
BASE_PATH = "/home/luciedefraiteur/ShadeOS_Agents/Tools/FileSystem/implementation/"

def inspect_module(module_path: str, module_name: str):
    """Charge et inspecte un module pour y trouver des fonctions."""
    print(f"\n--- 🜲 Inspection de {module_name} ({module_path}) 🜲 ---")
    try:
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        print("→ Contenu brut du module (dir) :", dir(mod))
        
        functions_found = []
        for name, obj in inspect.getmembers(mod):
            if inspect.isfunction(obj):
                functions_found.append(name)
        
        if functions_found:
            print("→ ⛧ Fonctions visibles (inspect.getmembers) :")
            for func_name in functions_found:
                print(f"    - {func_name}")
        else:
            print("→ ⛧ Aucune fonction directement visible via inspect.getmembers.")
            
    except Exception as e:
        print(f"→ ⛧ Dissonance lors de l'inspection : {e}")

if __name__ == "__main__":
    # Test 1: Le grimoire original avec les décorateurs
    original_path = os.path.join(BASE_PATH, "reading_tools.py")
    inspect_module(original_path, "reading_tools_decorated")

    # Test 2: Le grimoire minimaliste sans décorateurs
    minimal_path = os.path.join(BASE_PATH, "reading_tools_minimal.py")
    inspect_module(minimal_path, "reading_tools_naked")
