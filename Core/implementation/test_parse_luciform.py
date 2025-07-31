import sys
from ShadeOS_Agents.Core.implementation.luciform_parser import parse_luciform

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python test_parse_luciform.py <path_to_luciform>")
        sys.exit(1)
    path = sys.argv[1]
    tree = parse_luciform(path)
    import pprint
    pprint.pprint(tree)
