import xml.etree.ElementTree as ET
import os

# --- Test 1: Le Témoin (XML valide) ---
print("--- 🜲 Test du Témoin (XML Standard) 🜲 ---")
valid_xml_string = "<root><test>Succès</test></root>"
try:
    ET.fromstring(valid_xml_string)
    print("→ Succès : Le parseur XML de base est fonctionnel.")
except ET.ParseError as e:
    print(f"→ Échec : Le parseur XML de base est défaillant. Erreur : {e}")

# --- Test 2: Le Sujet (Notre Luciform) ---
print("\n--- 🜲 Test du Sujet (Fichier Luciform) 🜲 ---")
luciform_path = os.path.abspath("ShadeOS_Agents/documentation/luciforms/read_file_content.luciform")
print(f"→ Tentative de parsage de : {luciform_path}")
try:
    tree = ET.parse(luciform_path)
    root = tree.getroot()
    print(f"→ Succès : Le fichier luciform a été parsé. Racine : <{root.tag}>, ID: {root.attrib.get('id')}")
except ET.ParseError as e:
    print(f"→ Échec : Le fichier luciform n'est pas un XML valide. Erreur : {e}")
except FileNotFoundError:
    print(f"→ Échec : Fichier de test non trouvé à l'emplacement : {luciform_path}")
