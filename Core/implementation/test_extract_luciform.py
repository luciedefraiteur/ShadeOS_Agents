import sys
from ShadeOS_Agents.Core.implementation.luciform_parser import parse_luciform
from ShadeOS_Agents.Core.implementation.tool_registry import _reconstruct_doc_from_tree

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python test_extract_luciform.py <path_to_luciform>")
        sys.exit(1)
    path = sys.argv[1]
    tree = parse_luciform(path)
    print("\n--- Arbre Parsé ---")
    import pprint
    pprint.pprint(tree)
    print("\n--- Extraction par _reconstruct_doc_from_tree ---")
    doc = _reconstruct_doc_from_tree(tree)
    pprint.pprint(doc)
