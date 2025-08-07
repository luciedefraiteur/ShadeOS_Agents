import ast
import importlib.util
import os
import sys

def get_stdlib_paths():
    stdlib_path = os.path.dirname(os.__file__)
    return [stdlib_path]

def classify_import(module_name):
    try:
        spec = importlib.util.find_spec(module_name)
        if spec is None or spec.origin is None:
            return "🔴 unknown (likely external)"
        if spec.origin == 'built-in':
            return "🟢 builtin"
        for stdlib_path in get_stdlib_paths():
            if spec.origin.startswith(stdlib_path):
                return "🟡 standard library"
        return "🔴 external"
    except Exception as e:
        return f"🔴 error: {e}"

def extract_imports(filepath):
    with open(filepath, "r") as f:
        tree = ast.parse(f.read(), filename=filepath)

    imports = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name.split('.')[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.add(node.module.split('.')[0])

    return sorted(imports)

def scan_file(filepath):
    print(f"📄 Scanning {filepath}")
    modules = extract_imports(filepath)
    for module in modules:
        status = classify_import(module)
        print(f" - {module:<20} → {status}")

# Exemple d'usage
if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python detect_imports.py <script.py>")
    else:
        scan_file(sys.argv[1])
