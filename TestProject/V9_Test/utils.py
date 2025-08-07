
#!/usr/bin/env python3
"""
Utilitaires pour le projet de test
"""

import time
import random
from typing import List

def generate_test_data(count: int = 10) -> List[Dict]:
    """Génère des données de test"""
    data = []
    for i in range(count):
        data.append({
            "id": i,
            "name": f"item_{i}",
            "value": random.randint(1, 100),
            "timestamp": time.time()
        })
    return data

def analyze_data(data: List[Dict]) -> Dict:
    """Analyse les données"""
    if not data:
        return {"error": "Aucune donnée"}
    
    values = [item["value"] for item in data]
    return {
        "count": len(data),
        "min_value": min(values),
        "max_value": max(values),
        "avg_value": sum(values) / len(values)
    }
