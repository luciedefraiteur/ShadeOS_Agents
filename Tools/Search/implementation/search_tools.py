import glob
import os
import sys

# Ajouter le chemin vers Alagareth-toolset pour importer _string_utils
_alagareth_toolset_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "Alagareth-toolset")
if _alagareth_toolset_path not in sys.path:
    sys.path.insert(0, _alagareth_toolset_path)

from _string_utils import _simple_text_search

def find_files(pattern: str, base_path: str = ".") -> list[str]:
    """Trouve des fichiers en utilisant un pattern glob."""
    # Assure que base_path est un chemin absolu pour glob
    abs_base_path = os.path.abspath(base_path)
    
    # Combine le chemin de base avec le pattern pour une recherche relative
    search_pattern = os.path.join(abs_base_path, pattern)
    
    # Utilise glob.glob pour trouver les fichiers. recursive=True est nécessaire pour **
    found_files = glob.glob(search_pattern, recursive=True)
    
    # Retourne les chemins relatifs à base_path si désiré, ou absolus
    return [os.path.relpath(f, start=abs_base_path) for f in found_files]

def search_in_files(pattern: str, search_path: str = ".", case_sensitive: bool = True) -> list[dict]:
    """Recherche un motif de texte simple dans les fichiers d'un répertoire (sans regex)."""
    results = []
    abs_search_path = os.path.abspath(search_path)

    # Si search_path est un fichier, le traiter directement
    if os.path.isfile(abs_search_path):
        files_to_search = [abs_search_path]
    # Sinon, parcourir le répertoire
    elif os.path.isdir(abs_search_path):
        files_to_search = []
        for root, _, files in os.walk(abs_search_path):
            for file in files:
                files_to_search.append(os.path.join(root, file))
    else:
        return [{"error": f"Le chemin de recherche '{search_path}' n'est ni un fichier ni un répertoire valide."}]

    for file_path in files_to_search:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line_num, line_content in enumerate(f, 1):
                    if _simple_text_search(line_content, pattern, case_sensitive):
                        results.append({
                            "file_path": os.path.relpath(file_path, start=abs_search_path),
                            "line_number": line_num,
                            "line_content": line_content.strip()
                        })
        except Exception as e:
            results.append({"error": f"Impossible de lire le fichier {file_path}: {e}"})
    return results
