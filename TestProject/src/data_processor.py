#!/usr/bin/env python3
"""
Processeur de Données - ARCHITECTURE PROBLÉMATIQUE
Les daemons doivent restructurer ce code mal organisé.
"""

import json
import csv

# Variables globales (mauvaise pratique)
processed_data = []
error_count = 0
total_processed = 0

def process_json_file(filename):
    """Traite un fichier JSON - fonction trop longue et mal structurée"""
    global processed_data, error_count, total_processed
    
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
        
        # Logique de traitement mélangée (devrait être séparée)
        for item in data:
            if 'name' in item and 'value' in item:
                # Validation inline (devrait être une méthode séparée)
                if isinstance(item['value'], (int, float)) and item['value'] > 0:
                    # Transformation inline (devrait être une méthode séparée)
                    processed_item = {
                        'name': item['name'].strip().upper(),
                        'value': item['value'] * 1.1,  # Augmentation de 10%
                        'processed': True,
                        'source': 'json'
                    }
                    processed_data.append(processed_item)
                    total_processed += 1
                else:
                    error_count += 1
                    print(f"Erreur: valeur invalide pour {item.get('name', 'inconnu')}")
            else:
                error_count += 1
                print(f"Erreur: item manque name ou value")
        
        return True
    except Exception as e:
        print(f"Erreur lors du traitement JSON: {e}")
        error_count += 1
        return False

def process_csv_file(filename):
    """Traite un fichier CSV - code dupliqué avec process_json_file"""
    global processed_data, error_count, total_processed
    
    try:
        with open(filename, 'r') as f:
            reader = csv.DictReader(f)
            
            # Code quasi-identique à process_json_file (duplication)
            for row in reader:
                if 'name' in row and 'value' in row:
                    try:
                        value = float(row['value'])
                        if value > 0:
                            processed_item = {
                                'name': row['name'].strip().upper(),
                                'value': value * 1.1,  # Même logique dupliquée
                                'processed': True,
                                'source': 'csv'
                            }
                            processed_data.append(processed_item)
                            total_processed += 1
                        else:
                            error_count += 1
                            print(f"Erreur: valeur invalide pour {row.get('name', 'inconnu')}")
                    except ValueError:
                        error_count += 1
                        print(f"Erreur: impossible de convertir la valeur pour {row.get('name', 'inconnu')}")
                else:
                    error_count += 1
                    print(f"Erreur: ligne manque name ou value")
        
        return True
    except Exception as e:
        print(f"Erreur lors du traitement CSV: {e}")
        error_count += 1
        return False

def get_statistics():
    """Retourne les statistiques - accès direct aux variables globales"""
    return {
        'total_processed': total_processed,
        'error_count': error_count,
        'success_rate': (total_processed / (total_processed + error_count)) * 100 if (total_processed + error_count) > 0 else 0,
        'data_count': len(processed_data)
    }

def export_processed_data(filename):
    """Exporte les données traitées - fonction monolithique"""
    try:
        # Logique d'export mélangée
        if filename.endswith('.json'):
            with open(filename, 'w') as f:
                json.dump(processed_data, f, indent=2)
        elif filename.endswith('.csv'):
            if processed_data:
                with open(filename, 'w', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=processed_data[0].keys())
                    writer.writeheader()
                    writer.writerows(processed_data)
        else:
            print("Format de fichier non supporté")
            return False
        
        return True
    except Exception as e:
        print(f"Erreur lors de l'export: {e}")
        return False

def reset_processor():
    """Remet à zéro le processeur - modification des variables globales"""
    global processed_data, error_count, total_processed
    processed_data = []
    error_count = 0
    total_processed = 0

# Fonction utilitaire mal placée
def validate_item(item):
    """Validation qui devrait être dans une classe"""
    return 'name' in item and 'value' in item and isinstance(item['value'], (int, float)) and item['value'] > 0

# Code de test mélangé avec la logique métier
def run_test():
    """Test rapide - devrait être dans un fichier de test"""
    reset_processor()
    
    # Création de données de test
    test_data = [
        {'name': 'item1', 'value': 10},
        {'name': 'item2', 'value': 20},
        {'name': 'item3', 'value': -5},  # Valeur invalide
    ]
    
    # Simulation de traitement
    for item in test_data:
        if validate_item(item):
            processed_item = {
                'name': item['name'].strip().upper(),
                'value': item['value'] * 1.1,
                'processed': True,
                'source': 'test'
            }
            processed_data.append(processed_item)
            total_processed += 1
        else:
            error_count += 1
    
    print("Test terminé:")
    print(get_statistics())

if __name__ == "__main__":
    run_test()
