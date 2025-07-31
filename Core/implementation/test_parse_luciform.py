import sys
import os
import pprint

# Ajoute le répertoire racine du projet au PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from Core.implementation.luciform_parser import parse_luciform

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python test_parse_luciform.py <path_to_luciform>")
        sys.exit(1)
    path = sys.argv[1]
    luciform_data = parse_luciform(path)
    pprint.pprint(luciform_data)