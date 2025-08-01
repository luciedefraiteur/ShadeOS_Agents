#!/usr/bin/env python3
"""
Utilitaires - CODE DUPLIQUÉ ET MAL ORGANISÉ
Les daemons doivent identifier et éliminer la duplication.
"""

import os
import json
from datetime import datetime

# Fonction de validation dupliquée (version 1)
def validate_string_v1(text):
    """Valide une chaîne - version 1"""
    if text is None:
        return False
    if not isinstance(text, str):
        return False
    if len(text.strip()) == 0:
        return False
    return True

# Fonction de validation dupliquée (version 2)
def validate_string_v2(input_text):
    """Valide une chaîne - version 2 (quasi-identique)"""
    if input_text is None:
        return False
    if not isinstance(input_text, str):
        return False
    if len(input_text.strip()) == 0:
        return False
    return True

# Fonction de validation dupliquée (version 3)
def is_valid_string(s):
    """Valide une chaîne - version 3 (encore une duplication)"""
    return s is not None and isinstance(s, str) and len(s.strip()) > 0

# Fonctions de formatage dupliquées
def format_name_v1(name):
    """Formate un nom - version 1"""
    if not validate_string_v1(name):
        return ""
    return name.strip().title()

def format_name_v2(name):
    """Formate un nom - version 2 (identique)"""
    if not validate_string_v2(name):
        return ""
    return name.strip().title()

def format_person_name(name):
    """Formate un nom de personne - version 3 (encore identique)"""
    if not is_valid_string(name):
        return ""
    return name.strip().title()

# Fonctions de logging dupliquées
def log_message_v1(message):
    """Log un message - version 1"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted_message = f"[{timestamp}] {message}"
    print(formatted_message)
    return formatted_message

def log_info(message):
    """Log une info - version 2 (quasi-identique)"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted_message = f"[{timestamp}] INFO: {message}"
    print(formatted_message)
    return formatted_message

def write_log(message):
    """Écrit un log - version 3 (encore similaire)"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted_message = f"[{timestamp}] LOG: {message}"
    print(formatted_message)
    return formatted_message

# Fonctions de fichier dupliquées
def read_json_file_v1(filepath):
    """Lit un fichier JSON - version 1"""
    try:
        if not os.path.exists(filepath):
            return None
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Erreur lecture JSON: {e}")
        return None

def load_json_data(filepath):
    """Charge des données JSON - version 2 (identique)"""
    try:
        if not os.path.exists(filepath):
            return None
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Erreur chargement JSON: {e}")
        return None

def get_json_content(filepath):
    """Récupère le contenu JSON - version 3 (encore identique)"""
    try:
        if not os.path.exists(filepath):
            return None
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Erreur récupération JSON: {e}")
        return None

# Fonctions d'écriture dupliquées
def write_json_file_v1(data, filepath):
    """Écrit un fichier JSON - version 1"""
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Erreur écriture JSON: {e}")
        return False

def save_json_data(data, filepath):
    """Sauvegarde des données JSON - version 2 (identique)"""
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Erreur sauvegarde JSON: {e}")
        return False

# Fonction utilitaire mal nommée
def do_stuff(x, y):
    """Fonction mal nommée qui fait une addition"""
    return x + y

# Fonction inutilement complexe
def complex_addition(a, b):
    """Addition inutilement complexe"""
    result = 0
    if a > 0:
        for i in range(a):
            result += 1
    elif a < 0:
        for i in range(abs(a)):
            result -= 1
    
    if b > 0:
        for i in range(b):
            result += 1
    elif b < 0:
        for i in range(abs(b)):
            result -= 1
    
    return result

# Constantes dupliquées
DEFAULT_TIMEOUT_V1 = 30
DEFAULT_TIMEOUT_V2 = 30
TIMEOUT_DEFAULT = 30

MAX_RETRIES_V1 = 3
MAX_RETRIES_V2 = 3
RETRY_LIMIT = 3

# Fonction de test mélangée
def test_utils():
    """Test des utilitaires - devrait être dans un fichier de test"""
    print("Test des validations:")
    print(f"validate_string_v1('test'): {validate_string_v1('test')}")
    print(f"validate_string_v2('test'): {validate_string_v2('test')}")
    print(f"is_valid_string('test'): {is_valid_string('test')}")
    
    print("\nTest des formatages:")
    print(f"format_name_v1('john doe'): {format_name_v1('john doe')}")
    print(f"format_name_v2('john doe'): {format_name_v2('john doe')}")
    print(f"format_person_name('john doe'): {format_person_name('john doe')}")

if __name__ == "__main__":
    test_utils()
