#!/usr/bin/env python3
"""
🔧 Générateur de Projet de Test Complexe

Génère un projet Python complexe avec des dépendances variées pour tester
le système d'analyse d'imports résilient.

Auteur: Alma (via Lucie Defraiteur)
Date: 2025-08-06
"""

import os
import random
import string
from pathlib import Path
from typing import List, Dict, Set, Optional, Any, Union, Callable
from dataclasses import dataclass, field
from abc import ABC, abstractmethod


@dataclass
class ModuleInfo:
    """Informations sur un module généré"""
    name: str
    path: str
    imports: List[str]
    complexity: int
    has_circular_deps: bool
    has_broken_deps: bool


class ComplexProjectGenerator:
    """Générateur de projet complexe pour tests"""
    
    def __init__(self, base_path: str = "TestProject/complex_test_project"):
        self.base_path = Path(base_path)
        self.modules: List[ModuleInfo] = []
        self.generated_files: Set[str] = set()
        
        # Configuration du projet
        self.project_structure = {
            'core': {
                'utils': ['string_utils', 'file_utils', 'math_utils'],
                'models': ['user', 'product', 'order'],
                'services': ['auth_service', 'payment_service', 'notification_service']
            },
            'api': {
                'v1': ['users', 'products', 'orders'],
                'v2': ['users_v2', 'products_v2', 'orders_v2']
            },
            'tests': {
                'unit': ['test_utils', 'test_models', 'test_services'],
                'integration': ['test_api_v1', 'test_api_v2']
            },
            'broken': {
                'missing': ['missing_module_1', 'missing_module_2'],
                'circular': ['circular_a', 'circular_b', 'circular_c']
            }
        }
    
    def generate_project(self, complexity_level: str = "medium") -> str:
        """Génère le projet de test complet"""
        
        print(f"🔧 Génération du projet de test complexe (niveau: {complexity_level})...")
        
        # Nettoyer le répertoire
        if self.base_path.exists():
            import shutil
            shutil.rmtree(self.base_path)
        
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        # Générer la structure
        self._generate_project_structure()
        
        # Générer les modules selon le niveau de complexité
        if complexity_level == "simple":
            self._generate_simple_modules()
        elif complexity_level == "medium":
            self._generate_medium_modules()
        elif complexity_level == "complex":
            self._generate_complex_modules()
        else:
            self._generate_medium_modules()
        
        # Générer les fichiers avec dépendances brisées
        self._generate_broken_dependencies()
        
        # Générer les imports circulaires
        self._generate_circular_dependencies()
        
        # Générer les fichiers de configuration
        self._generate_config_files()
        
        # Générer le README
        self._generate_readme()
        
        print(f"✅ Projet généré dans {self.base_path}")
        print(f"📊 Statistiques: {len(self.modules)} modules, {len(self.generated_files)} fichiers")
        
        return str(self.base_path)
    
    def _generate_project_structure(self):
        """Génère la structure de répertoires"""
        
        for category, subcategories in self.project_structure.items():
            category_path = self.base_path / category
            category_path.mkdir(exist_ok=True)
            
            for subcategory, modules in subcategories.items():
                subcategory_path = category_path / subcategory
                subcategory_path.mkdir(exist_ok=True)
                
                # Créer __init__.py
                init_file = subcategory_path / "__init__.py"
                init_file.write_text(self._generate_init_content(category, subcategory))
                self.generated_files.add(str(init_file))
    
    def _generate_simple_modules(self):
        """Génère des modules simples"""
        
        for category, subcategories in self.project_structure.items():
            for subcategory, modules in subcategories.items():
                for module in modules:
                    if category != "broken":  # Pas de modules brisés pour le niveau simple
                        self._generate_module(category, subcategory, module, complexity="simple")
    
    def _generate_medium_modules(self):
        """Génère des modules de complexité moyenne"""
        
        for category, subcategories in self.project_structure.items():
            for subcategory, modules in subcategories.items():
                for module in modules:
                    if category != "broken":
                        self._generate_module(category, subcategory, module, complexity="medium")
        
        # Ajouter quelques modules brisés
        self._generate_module("broken", "missing", "missing_module_1", complexity="medium", broken=True)
    
    def _generate_complex_modules(self):
        """Génère des modules complexes"""
        
        for category, subcategories in self.project_structure.items():
            for subcategory, modules in subcategories.items():
                for module in modules:
                    self._generate_module(category, subcategory, module, complexity="complex")
    
    def _generate_module(self, category: str, subcategory: str, module: str, 
                        complexity: str = "medium", broken: bool = False):
        """Génère un module Python"""
        
        module_path = self.base_path / category / subcategory / f"{module}.py"
        
        # Générer le contenu selon la complexité
        if complexity == "simple":
            content = self._generate_simple_module_content(category, subcategory, module)
        elif complexity == "medium":
            content = self._generate_medium_module_content(category, subcategory, module)
        else:  # complex
            content = self._generate_complex_module_content(category, subcategory, module)
        
        # Ajouter des imports brisés si nécessaire
        if broken:
            content = self._add_broken_imports(content)
        
        module_path.write_text(content)
        self.generated_files.add(str(module_path))
        
        # Enregistrer les informations du module
        imports = self._extract_imports_from_content(content)
        self.modules.append(ModuleInfo(
            name=module,
            path=str(module_path),
            imports=imports,
            complexity=len(imports),
            has_circular_deps=False,
            has_broken_deps=broken
        ))
    
    def _generate_simple_module_content(self, category: str, subcategory: str, module: str) -> str:
        """Génère le contenu d'un module simple"""
        
        imports = [
            "import os",
            "import sys",
            "from typing import Dict, List"
        ]
        
        # Ajouter quelques imports locaux
        if category == "core" and subcategory == "utils":
            imports.append("from ..models.user import User")
        elif category == "api" and subcategory == "v1":
            imports.append("from ...core.services.auth_service import AuthService")
        
        content = f'''#!/usr/bin/env python3
"""
Module simple: {module}
Catégorie: {category}.{subcategory}
"""

{chr(10).join(imports)}

class {module.title().replace('_', '')}:
    """Classe simple pour {module}"""
    
    def __init__(self):
        self.name = "{module}"
        self.category = "{category}"
        self.subcategory = "{subcategory}"
    
    def get_info(self) -> Dict[str, str]:
        """Retourne les informations du module"""
        return {{
            "name": self.name,
            "category": self.category,
            "subcategory": self.subcategory
        }}

def create_{module}():
    """Fonction de création"""
    return {module.title().replace('_', '')}()

if __name__ == "__main__":
    instance = create_{module}()
    print(instance.get_info())
'''
        return content
    
    def _generate_medium_module_content(self, category: str, subcategory: str, module: str) -> str:
        """Génère le contenu d'un module de complexité moyenne"""
        
        imports = [
            "import os",
            "import sys",
            "import json",
            "import logging",
            "from typing import Dict, List, Optional, Any",
            "from pathlib import Path",
            "from datetime import datetime"
        ]
        
        # Ajouter des imports locaux selon la catégorie
        if category == "core":
            if subcategory == "utils":
                imports.extend([
                    "from ..models.user import User",
                    "from ..models.product import Product",
                    "from .string_utils import StringUtils"
                ])
            elif subcategory == "models":
                imports.extend([
                    "from ..utils.string_utils import StringUtils",
                    "from ..services.auth_service import AuthService"
                ])
            elif subcategory == "services":
                imports.extend([
                    "from ..models.user import User",
                    "from ..utils.file_utils import FileUtils"
                ])
        elif category == "api":
            imports.extend([
                "from ...core.models.user import User",
                "from ...core.services.auth_service import AuthService",
                "from ...core.utils.string_utils import StringUtils"
            ])
        
        content = f'''#!/usr/bin/env python3
"""
Module de complexité moyenne: {module}
Catégorie: {category}.{subcategory}
"""

{chr(10).join(imports)}

logger = logging.getLogger(__name__)

class {module.title().replace('_', '')}:
    """Classe de complexité moyenne pour {module}"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.name = "{module}"
        self.category = "{category}"
        self.subcategory = "{subcategory}"
        self.config = config or {{}}
        self.created_at = datetime.now()
        
        logger.info(f"Initialisation de {{self.name}}")
    
    def process_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Traite les données"""
        logger.info(f"Traitement des données pour {{self.name}}")
        
        result = {{
            "module": self.name,
            "processed_at": datetime.now().isoformat(),
            "data_size": len(str(data)),
            "category": self.category
        }}
        
        return result
    
    def validate_input(self, input_data: Any) -> bool:
        """Valide les données d'entrée"""
        if not input_data:
            logger.warning("Données d'entrée vides")
            return False
        
        return True
    
    def get_statistics(self) -> Dict[str, Any]:
        """Retourne les statistiques du module"""
        return {{
            "name": self.name,
            "category": self.category,
            "subcategory": self.subcategory,
            "created_at": self.created_at.isoformat(),
            "config_keys": list(self.config.keys())
        }}

def create_{module}(config: Optional[Dict[str, Any]] = None):
    """Fonction de création avec configuration"""
    return {module.title().replace('_', '')}(config)

def process_with_{module}(data: Dict[str, Any], config: Optional[Dict[str, Any]] = None):
    """Fonction utilitaire de traitement"""
    instance = create_{module}(config)
    
    if instance.validate_input(data):
        return instance.process_data(data)
    else:
        raise ValueError("Données d'entrée invalides")

if __name__ == "__main__":
    # Test du module
    test_data = {{"test": "data", "value": 42}}
    result = process_with_{module}(test_data)
    print(json.dumps(result, indent=2))
'''
        return content
    
    def _generate_complex_module_content(self, category: str, subcategory: str, module: str) -> str:
        """Génère le contenu d'un module complexe"""
        
        imports = [
            "import os",
            "import sys",
            "import json",
            "import logging",
            "import asyncio",
            "import threading",
            "from typing import Dict, List, Optional, Any, Union, Callable",
            "from pathlib import Path",
            "from datetime import datetime, timedelta",
            "from dataclasses import dataclass, field",
            "from abc import ABC, abstractmethod"
        ]
        
        # Ajouter de nombreux imports locaux
        if category == "core":
            imports.extend([
                "from ..models.user import User",
                "from ..models.product import Product", 
                "from ..models.order import Order",
                "from ..utils.string_utils import StringUtils",
                "from ..utils.file_utils import FileUtils",
                "from ..utils.math_utils import MathUtils",
                "from ..services.auth_service import AuthService",
                "from ..services.payment_service import PaymentService"
            ])
        elif category == "api":
            imports.extend([
                "from ...core.models.user import User",
                "from ...core.models.product import Product",
                "from ...core.services.auth_service import AuthService",
                "from ...core.services.payment_service import PaymentService",
                "from ...core.utils.string_utils import StringUtils",
                "from ...core.utils.file_utils import FileUtils"
            ])
        
        content = f'''#!/usr/bin/env python3
"""
Module complexe: {module}
Catégorie: {category}.{subcategory}
"""

{chr(10).join(imports)}

logger = logging.getLogger(__name__)

@dataclass
class {module.title().replace('_', '')}Config:
    """Configuration pour {module.title().replace('_', '')}"""
    
    name: str = "{module}"
    category: str = "{category}"
    subcategory: str = "{subcategory}"
    max_retries: int = 3
    timeout: float = 30.0
    cache_enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

class {module.title().replace('_', '')}Base(ABC):
    """Classe de base abstraite pour {module}"""
    
    @abstractmethod
    async def initialize(self) -> bool:
        """Initialise le module"""
        pass
    
    @abstractmethod
    async def process_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Traite les données de manière asynchrone"""
        pass
    
    @abstractmethod
    def validate_config(self, config: {module.title().replace('_', '')}Config) -> bool:
        """Valide la configuration"""
        pass

class {module.title().replace('_', '')}({module.title().replace('_', '')}Base):
    """Classe complexe pour {module} avec gestion asynchrone"""
    
    def __init__(self, config: Optional[{module.title().replace('_', '')}Config] = None):
        self.config = config or {module.title().replace('_', '')}Config()
        self.initialized = False
        self.processing_lock = threading.Lock()
        self.cache: Dict[str, Any] = {{}}
        self.stats = {{
            "processed_items": 0,
            "errors": 0,
            "start_time": datetime.now(),
            "last_processed": None
        }}
        
        logger.info(f"Initialisation de {{self.config.name}}")
    
    async def initialize(self) -> bool:
        """Initialise le module de manière asynchrone"""
        try:
            logger.info(f"Initialisation asynchrone de {{self.config.name}}")
            
            # Simulation d'initialisation asynchrone
            await asyncio.sleep(0.1)
            
            self.initialized = True
            logger.info(f"{{self.config.name}} initialisé avec succès")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation de {{self.config.name}}: {{e}}")
            return False
    
    async def process_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Traite les données de manière asynchrone"""
        
        if not self.initialized:
            await self.initialize()
        
        with self.processing_lock:
            try:
                logger.info(f"Traitement asynchrone des données pour {{self.config.name}}")
                
                # Simulation de traitement complexe
                await asyncio.sleep(0.05)
                
                result = {{
                    "module": self.config.name,
                    "processed_at": datetime.now().isoformat(),
                    "data_size": len(str(data)),
                    "category": self.config.category,
                    "cache_hit": self.config.cache_enabled and str(data) in self.cache,
                    "processing_time": 0.05
                }}
                
                # Mise en cache si activé
                if self.config.cache_enabled:
                    self.cache[str(data)] = result
                
                # Mise à jour des statistiques
                self.stats["processed_items"] += 1
                self.stats["last_processed"] = datetime.now()
                
                return result
                
            except Exception as e:
                logger.error(f"Erreur lors du traitement: {{e}}")
                self.stats["errors"] += 1
                raise
    
    def validate_config(self, config: {module.title().replace('_', '')}Config) -> bool:
        """Valide la configuration"""
        if not config.name:
            logger.error("Nom de configuration manquant")
            return False
        
        if config.max_retries < 0:
            logger.error("Nombre de tentatives invalide")
            return False
        
        if config.timeout <= 0:
            logger.error("Timeout invalide")
            return False
        
        return True
    
    def get_statistics(self) -> Dict[str, Any]:
        """Retourne les statistiques détaillées"""
        return {{
            "config": {{
                "name": self.config.name,
                "category": self.config.category,
                "subcategory": self.config.subcategory,
                "max_retries": self.config.max_retries,
                "timeout": self.config.timeout,
                "cache_enabled": self.config.cache_enabled
            }},
            "stats": self.stats,
            "cache_size": len(self.cache),
            "initialized": self.initialized
        }}
    
    def clear_cache(self):
        """Vide le cache"""
        self.cache.clear()
        logger.info("Cache vidé")

async def create_{module}_async(config: Optional[{module.title().replace('_', '')}Config] = None):
    """Fonction de création asynchrone"""
    instance = {module.title().replace('_', '')}(config)
    await instance.initialize()
    return instance

async def process_with_{module}_async(data: Dict[str, Any], config: Optional[{module.title().replace('_', '')}Config] = None):
    """Fonction utilitaire de traitement asynchrone"""
    instance = await create_{module}_async(config)
    return await instance.process_data(data)

def create_{module}(config: Optional[{module.title().replace('_', '')}Config] = None):
    """Fonction de création synchrone"""
    return {module.title().replace('_', '')}(config)

if __name__ == "__main__":
    # Test du module complexe
    async def test_module():
        config = {module.title().replace('_', '')}Config(
            max_retries=5,
            timeout=60.0,
            cache_enabled=True
        )
        
        test_data = {{"test": "complex_data", "value": 42, "nested": {{"key": "value"}}}}
        
        try:
            result = await process_with_{module}_async(test_data, config)
            print(json.dumps(result, indent=2))
            
            # Afficher les statistiques
            instance = create_{module}(config)
            stats = instance.get_statistics()
            print("\\nStatistiques:")
            print(json.dumps(stats, indent=2, default=str))
            
        except Exception as e:
            print(f"Erreur: {{e}}")
    
    # Exécuter le test
    asyncio.run(test_module())
'''
        return content
    
    def _add_broken_imports(self, content: str) -> str:
        """Ajoute des imports brisés au contenu"""
        
        broken_imports = [
            "from missing_module import MissingClass",
            "import nonexistent_package",
            "from .broken_module import BrokenClass",
            "from ..missing_folder.missing_file import MissingFunction"
        ]
        
        # Ajouter les imports brisés après les imports normaux
        import_lines = content.split('\n')
        insert_index = 0
        
        for i, line in enumerate(import_lines):
            if line.startswith('import ') or line.startswith('from '):
                insert_index = i + 1
        
        # Insérer les imports brisés
        for broken_import in broken_imports:
            import_lines.insert(insert_index, broken_import)
            insert_index += 1
        
        return '\n'.join(import_lines)
    
    def _generate_broken_dependencies(self):
        """Génère des fichiers avec des dépendances brisées"""
        
        broken_content = '''#!/usr/bin/env python3
"""
Module avec dépendances brisées
"""

# Imports brisés intentionnels
from missing_module import MissingClass
import nonexistent_package
from .broken_module import BrokenClass
from ..missing_folder.missing_file import MissingFunction

class BrokenModule:
    """Module avec des dépendances brisées"""
    
    def __init__(self):
        self.name = "broken_module"
    
    def broken_function(self):
        """Fonction qui utilise des imports brisés"""
        try:
            # Ces appels vont échouer
            missing = MissingClass()
            nonexistent = nonexistent_package.some_function()
            broken = BrokenClass()
            missing_func = MissingFunction()
        except ImportError as e:
            print(f"ImportError attendu: {e}")
        except Exception as e:
            print(f"Erreur: {e}")

if __name__ == "__main__":
    module = BrokenModule()
    module.broken_function()
'''
        
        # Créer des fichiers avec des dépendances brisées
        broken_files = [
            "broken_module_1.py",
            "broken_module_2.py",
            "circular_a.py",
            "circular_b.py",
            "circular_c.py"
        ]
        
        for broken_file in broken_files:
            file_path = self.base_path / "broken" / "missing" / broken_file
            file_path.write_text(broken_content)
            self.generated_files.add(str(file_path))
    
    def _generate_circular_dependencies(self):
        """Génère des fichiers avec des imports circulaires"""
        
        # Module A qui importe B
        circular_a_content = '''#!/usr/bin/env python3
"""
Module A avec import circulaire vers B
"""

from .circular_b import CircularB

class CircularA:
    def __init__(self):
        self.name = "CircularA"
        self.b_instance = CircularB()
    
    def get_info(self):
        return {"name": self.name, "depends_on": "CircularB"}
'''
        
        # Module B qui importe C
        circular_b_content = '''#!/usr/bin/env python3
"""
Module B avec import circulaire vers C
"""

from .circular_c import CircularC

class CircularB:
    def __init__(self):
        self.name = "CircularB"
        self.c_instance = CircularC()
    
    def get_info(self):
        return {"name": self.name, "depends_on": "CircularC"}
'''
        
        # Module C qui importe A (cycle complet)
        circular_c_content = '''#!/usr/bin/env python3
"""
Module C avec import circulaire vers A
"""

from .circular_a import CircularA

class CircularC:
    def __init__(self):
        self.name = "CircularC"
        self.a_instance = CircularA()
    
    def get_info(self):
        return {"name": self.name, "depends_on": "CircularA"}
'''
        
        # Écrire les fichiers
        circular_files = [
            ("circular_a.py", circular_a_content),
            ("circular_b.py", circular_b_content),
            ("circular_c.py", circular_c_content)
        ]
        
        for filename, content in circular_files:
            file_path = self.base_path / "broken" / "circular" / filename
            file_path.write_text(content)
            self.generated_files.add(str(file_path))
    
    def _generate_init_content(self, category: str, subcategory: str) -> str:
        """Génère le contenu d'un fichier __init__.py"""
        
        return f'''#!/usr/bin/env python3
"""
Package: {category}.{subcategory}
"""

__version__ = "1.0.0"
__author__ = "Test Generator"

# Imports des modules du package
try:
    from . import *
except ImportError as e:
    print(f"Warning: Erreur d'import dans {category}.{subcategory}: {{e}}")
'''
    
    def _generate_config_files(self):
        """Génère les fichiers de configuration"""
        
        # requirements.txt
        requirements_content = '''# Requirements pour le projet de test
pytest>=7.0.0
pytest-asyncio>=0.21.0
black>=22.0.0
flake8>=5.0.0
mypy>=1.0.0
'''
        
        requirements_file = self.base_path / "requirements.txt"
        requirements_file.write_text(requirements_content)
        self.generated_files.add(str(requirements_file))
        
        # setup.py
        setup_content = '''#!/usr/bin/env python3
from setuptools import setup, find_packages

setup(
    name="complex-test-project",
    version="1.0.0",
    description="Projet de test complexe pour l'analyse d'imports",
    packages=find_packages(),
    install_requires=[
        "pytest>=7.0.0",
        "pytest-asyncio>=0.21.0",
    ],
    python_requires=">=3.8",
)
'''
        
        setup_file = self.base_path / "setup.py"
        setup_file.write_text(setup_content)
        self.generated_files.add(str(setup_file))
    
    def _generate_readme(self):
        """Génère le README du projet"""
        
        readme_content = f'''# Projet de Test Complexe

Ce projet a été généré automatiquement pour tester le système d'analyse d'imports résilient.

## Structure

```
{self.base_path.name}/
├── core/
│   ├── utils/
│   ├── models/
│   └── services/
├── api/
│   ├── v1/
│   └── v2/
├── tests/
│   ├── unit/
│   └── integration/
└── broken/
    ├── missing/
    └── circular/
```

## Caractéristiques

- **Modules simples** : Imports basiques
- **Modules moyens** : Imports locaux et gestion d'erreurs
- **Modules complexes** : Imports multiples et gestion asynchrone
- **Dépendances brisées** : Imports vers des modules inexistants
- **Imports circulaires** : Cycles de dépendances

## Tests

```bash
# Analyser le projet
python Core/Partitioner/import_analyzer.py {self.base_path}/core/utils/string_utils.py

# Tester avec l'analyseur résilient
python -c "
from Core.Partitioner.resilient_import_analyzer import get_resilient_import_analyzer
import asyncio

async def test():
    analyzer = get_resilient_import_analyzer()
    result = await analyzer.analyze_imports_resilient('{self.base_path}/core/utils/string_utils.py')
    print(result)

asyncio.run(test())
"
```

## Statistiques

- **Modules générés** : {len(self.modules)}
- **Fichiers créés** : {len(self.generated_files)}
- **Dépendances brisées** : Oui
- **Imports circulaires** : Oui

Généré le : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
'''
        
        readme_file = self.base_path / "README.md"
        readme_file.write_text(readme_content)
        self.generated_files.add(str(readme_file))
    
    def _extract_imports_from_content(self, content: str) -> List[str]:
        """Extrait les imports du contenu d'un fichier"""
        
        imports = []
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if line.startswith('import ') or line.startswith('from '):
                import_stmt = line.split('#')[0].strip()
                if import_stmt:
                    imports.append(import_stmt)
        
        return imports
    
    def get_project_statistics(self) -> Dict[str, Any]:
        """Retourne les statistiques du projet généré"""
        
        return {
            'project_path': str(self.base_path),
            'total_modules': len(self.modules),
            'total_files': len(self.generated_files),
            'modules_by_complexity': {
                'simple': len([m for m in self.modules if m.complexity < 5]),
                'medium': len([m for m in self.modules if 5 <= m.complexity < 15]),
                'complex': len([m for m in self.modules if m.complexity >= 15])
            },
            'broken_dependencies': len([m for m in self.modules if m.has_broken_deps]),
            'circular_dependencies': len([m for m in self.modules if m.has_circular_deps]),
            'average_imports_per_module': sum(m.complexity for m in self.modules) / len(self.modules) if self.modules else 0
        }


def main():
    """Point d'entrée principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Générateur de projet de test complexe")
    parser.add_argument('--complexity', choices=['simple', 'medium', 'complex'], 
                       default='medium', help='Niveau de complexité')
    parser.add_argument('--output', default='TestProject/complex_test_project',
                       help='Répertoire de sortie')
    
    args = parser.parse_args()
    
    # Générer le projet
    generator = ComplexProjectGenerator(args.output)
    project_path = generator.generate_project(args.complexity)
    
    # Afficher les statistiques
    stats = generator.get_project_statistics()
    print("\n📊 Statistiques du projet généré:")
    for key, value in stats.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    main() 