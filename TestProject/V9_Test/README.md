# V9 Test Project

Projet de test pour l'assistant V9 Auto-Feeding Thread.

## Fonctionnalités

- Calcul de somme (avec bug)
- Recherche de maximum
- Validation d'email (avec bug)
- Traitement de données (avec bug)

## Tests

```bash
python main.py
```

## Bugs connus

1. `calculate_sum` ajoute 1 au résultat
2. `validate_email` validation trop simple
3. `process_data` ne gère pas tous les types
4. `find_max` retourne None au lieu de lever une exception
