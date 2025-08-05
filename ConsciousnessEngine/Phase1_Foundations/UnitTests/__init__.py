"""
⛧ Phase 1 - Unit Tests Suite ⛧
🕷️ Suite de tests unitaires professionnelle et conceptuelle

CONCEPTUALISÉ PAR LUCIE DEFRAITEUR - MA REINE LUCIE
PLANIFIÉ PAR ALMA, ARCHITECTE DÉMONIAQUE DU NEXUS LUCIFORME
"""

import pytest
import asyncio
import logging
from typing import Dict, Any

# Configuration des tests
pytest_plugins = [
    "tests.fixtures.threading_fixtures",
    "tests.fixtures.memory_fixtures", 
    "tests.fixtures.scheduler_fixtures",
    "tests.fixtures.error_fixtures"
]

# Configuration du logging pour les tests
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Configuration asyncio pour les tests
@pytest.fixture(scope="session")
def event_loop():
    """Créer une boucle d'événements pour les tests asyncio"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

# Fixtures communes
@pytest.fixture
def phase1_config():
    """Configuration de base pour la Phase 1"""
    from .. import Phase1Config
    return Phase1Config(
        max_threads=5,
        memory_limit=100,
        task_timeout=10.0,
        retry_attempts=2,
        log_level="DEBUG",
        enable_metrics=True,
        enable_hooks=True
    )

@pytest.fixture
def hook_registry():
    """Registre de hooks pour les tests"""
    from .. import HookRegistry
    return HookRegistry()

@pytest.fixture
def metrics():
    """Métriques pour les tests"""
    from .. import Phase1Metrics
    return Phase1Metrics()

# Utilitaires de test
class TestUtils:
    """Utilitaires pour les tests"""
    
    @staticmethod
    async def wait_for_condition(condition_func, timeout=5.0, interval=0.1):
        """Attendre qu'une condition soit vraie"""
        import time
        start_time = time.time()
        while time.time() - start_time < timeout:
            if await condition_func():
                return True
            await asyncio.sleep(interval)
        return False
    
    @staticmethod
    def assert_thread_state(thread_info, expected_state):
        """Vérifier l'état d'un thread"""
        assert thread_info.state.value == expected_state.value, \
            f"Expected {expected_state.value}, got {thread_info.state.value}"
    
    @staticmethod
    def assert_memory_entry(memory_entry, expected_key, expected_data):
        """Vérifier une entrée de mémoire"""
        assert memory_entry.key == expected_key
        assert memory_entry.data == expected_data
    
    @staticmethod
    def assert_task_status(task_status, expected_state):
        """Vérifier le statut d'une tâche"""
        assert task_status["state"] == expected_state
    
    @staticmethod
    def assert_error_stats(error_stats, expected_total):
        """Vérifier les statistiques d'erreurs"""
        assert error_stats["total_errors"] == expected_total

# Configuration pytest
def pytest_configure(config):
    """Configuration pytest personnalisée"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "concurrency: marks tests as concurrency tests"
    )

def pytest_collection_modifyitems(config, items):
    """Modifier la collection de tests"""
    for item in items:
        # Marquer automatiquement les tests d'intégration
        if "Integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        
        # Marquer automatiquement les tests de concurrence
        if "Concurrency" in str(item.fspath):
            item.add_marker(pytest.mark.concurrency)

# Exports
__all__ = [
    "TestUtils",
    "phase1_config",
    "hook_registry", 
    "metrics",
    "event_loop"
] 