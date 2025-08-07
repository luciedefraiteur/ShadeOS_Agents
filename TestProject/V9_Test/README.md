
# Projet de Test V9

Ce projet a été créé pour tester le V9_AutoFeedingThreadAgent.

## Structure

- `main.py` : Classe principale du projet
- `utils.py` : Utilitaires et fonctions d'aide
- `test_main.py` : Tests unitaires
- `README.md` : Documentation

## Utilisation

```python
from main import TestProject
from utils import generate_test_data

project = TestProject()
data = generate_test_data(10)
project.add_data("test_data", data)
```

## Tests

```bash
python test_main.py
```
