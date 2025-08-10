"""
Système d'initialisation singleton pour MemoryEngine
Gère l'initialisation automatique de Neo4j et des composants requis
"""

import logging
from typing import Optional, Dict, Any
from threading import Lock

from .neo4j_manager import ensure_neo4j_running, get_neo4j_manager

logger = logging.getLogger(__name__)

class MemoryEngineInitializer:
    """Initialiseur singleton pour MemoryEngine"""
    
    def __init__(self):
        self._initialized = False
        self._initialization_lock = Lock()
        self._neo4j_available = False
        self._initialization_error: Optional[str] = None
        self._connection_info: Dict[str, Any] = {}
    
    def initialize(self, force_neo4j: bool = False) -> bool:
        """
        Initialise MemoryEngine et ses dépendances
        
        Args:
            force_neo4j: Si True, échoue si Neo4j n'est pas disponible
            
        Returns:
            True si l'initialisation a réussi
        """
        with self._initialization_lock:
            if self._initialized:
                logger.info("MemoryEngine déjà initialisé")
                return True
            
            logger.info("Initialisation de MemoryEngine...")
            
            # Vérifier et démarrer Neo4j
            neo4j_success, neo4j_message = ensure_neo4j_running()
            
            if neo4j_success:
                self._neo4j_available = True
                self._connection_info = get_neo4j_manager().get_connection_info()
                logger.info(f"Neo4j disponible: {neo4j_message}")
                logger.info(f"Connexion: {self._connection_info}")
            else:
                self._neo4j_available = False
                self._initialization_error = f"Neo4j non disponible: {neo4j_message}"
                logger.warning(self._initialization_error)
                
                if force_neo4j:
                    logger.error("Neo4j requis mais non disponible")
                    return False
            
            # Ici on pourrait ajouter d'autres vérifications d'initialisation
            # (par exemple, vérifier les permissions de fichiers, etc.)
            
            self._initialized = True
            logger.info("MemoryEngine initialisé avec succès")
            return True
    
    def is_initialized(self) -> bool:
        """Vérifie si MemoryEngine est initialisé"""
        return self._initialized
    
    def is_neo4j_available(self) -> bool:
        """Vérifie si Neo4j est disponible"""
        return self._neo4j_available
    
    def get_connection_info(self) -> Dict[str, Any]:
        """Retourne les informations de connexion"""
        return self._connection_info.copy()
    
    def get_initialization_error(self) -> Optional[str]:
        """Retourne l'erreur d'initialisation s'il y en a une"""
        return self._initialization_error
    
    def reset(self):
        """Réinitialise l'état (pour les tests)"""
        with self._initialization_lock:
            self._initialized = False
            self._neo4j_available = False
            self._initialization_error = None
            self._connection_info = {}

# Instance singleton globale
_initializer: Optional[MemoryEngineInitializer] = None
_initializer_lock = Lock()

def get_initializer() -> MemoryEngineInitializer:
    """Retourne l'instance singleton de l'initialiseur"""
    global _initializer
    with _initializer_lock:
        if _initializer is None:
            _initializer = MemoryEngineInitializer()
        return _initializer

def ensure_initialized(force_neo4j: bool = False) -> bool:
    """
    S'assure que MemoryEngine est initialisé
    
    Args:
        force_neo4j: Si True, échoue si Neo4j n'est pas disponible
        
    Returns:
        True si l'initialisation a réussi
    """
    initializer = get_initializer()
    return initializer.initialize(force_neo4j=force_neo4j)

def is_neo4j_available() -> bool:
    """Vérifie si Neo4j est disponible"""
    initializer = get_initializer()
    if not initializer.is_initialized():
        initializer.initialize()
    return initializer.is_neo4j_available()

def get_neo4j_connection_info() -> Dict[str, Any]:
    """Retourne les informations de connexion Neo4j"""
    initializer = get_initializer()
    if not initializer.is_initialized():
        initializer.initialize()
    return initializer.get_connection_info() 