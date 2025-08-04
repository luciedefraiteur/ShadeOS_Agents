"""
Gestionnaire Neo4j pour MemoryEngine
Vérifie et lance automatiquement le conteneur Neo4j si nécessaire
"""

import subprocess
import time
import logging
from typing import Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class Neo4jStatus:
    """Statut du conteneur Neo4j"""
    is_running: bool
    container_id: Optional[str] = None
    ports: Optional[str] = None
    error_message: Optional[str] = None

class Neo4jManager:
    """Gestionnaire pour le conteneur Neo4j"""
    
    CONTAINER_NAME = "neo4j-fractal-memory"
    BOLT_PORT = 7687
    BROWSER_PORT = 7474
    
    # Configuration par défaut pour un environnement de développement local
    DEFAULT_PASSWORD = "fractal-memory-dev"
    DEFAULT_USER = "neo4j"
    DEFAULT_IMAGE = "neo4j:5.15"
    
    def __init__(self):
        self._status: Optional[Neo4jStatus] = None
    
    def check_status(self) -> Neo4jStatus:
        """Vérifie le statut du conteneur Neo4j"""
        try:
            # D'abord vérifier si le conteneur est en cours d'exécution
            running_result = subprocess.run(
                ["docker", "ps", "--filter", f"name={self.CONTAINER_NAME}"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if running_result.returncode == 0 and len(running_result.stdout.strip().split('\n')) > 1:
                # Le conteneur est en cours d'exécution
                lines = running_result.stdout.strip().split('\n')
                container_line = lines[1]
                parts = container_line.split()
                
                if len(parts) >= 7:
                    container_id = parts[0]
                    ports = " ".join(parts[6:]) if len(parts) > 6 else ""
                    
                    return Neo4jStatus(
                        is_running=True,
                        container_id=container_id,
                        ports=ports,
                        error_message=None
                    )
            
            # Si pas en cours d'exécution, vérifier s'il existe
            result = subprocess.run(
                ["docker", "ps", "-a", "--filter", f"name={self.CONTAINER_NAME}"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                return Neo4jStatus(
                    is_running=False,
                    error_message=f"Erreur Docker: {result.stderr}"
                )
            
            lines = result.stdout.strip().split('\n')
            if len(lines) < 2:  # Pas de conteneur trouvé
                return Neo4jStatus(
                    is_running=False,
                    error_message=f"Conteneur {self.CONTAINER_NAME} non trouvé"
                )
            
            # Parser la ligne du conteneur (ignorer l'en-tête)
            container_line = lines[1]
            parts = container_line.split()
            
            if len(parts) < 7:
                return Neo4jStatus(
                    is_running=False,
                    error_message="Format de sortie Docker inattendu"
                )
            
            container_id = parts[0]
            status = parts[6]  # Statut du conteneur
            ports = " ".join(parts[7:]) if len(parts) > 7 else ""
            
            is_running = status.lower() == "up"
            
            return Neo4jStatus(
                is_running=is_running,
                container_id=container_id,
                ports=ports,
                error_message=None if is_running else f"Conteneur arrêté (status: {status})"
            )
            
        except subprocess.TimeoutExpired:
            return Neo4jStatus(
                is_running=False,
                error_message="Timeout lors de la vérification Docker"
            )
        except FileNotFoundError:
            return Neo4jStatus(
                is_running=False,
                error_message="Docker non installé ou non accessible"
            )
        except Exception as e:
            return Neo4jStatus(
                is_running=False,
                error_message=f"Erreur inattendue: {str(e)}"
            )
    
    def _pull_image(self) -> Tuple[bool, str]:
        """Télécharge l'image Neo4j si nécessaire"""
        try:
            logger.info(f"Téléchargement de l'image {self.DEFAULT_IMAGE}...")
            
            result = subprocess.run(
                ["docker", "pull", self.DEFAULT_IMAGE],
                capture_output=True,
                text=True,
                timeout=120  # 2 minutes pour le téléchargement
            )
            
            if result.returncode != 0:
                return False, f"Erreur lors du téléchargement: {result.stderr}"
            
            logger.info("Image Neo4j téléchargée avec succès")
            return True, "Image téléchargée"
            
        except subprocess.TimeoutExpired:
            return False, "Timeout lors du téléchargement de l'image"
        except Exception as e:
            return False, f"Erreur inattendue: {str(e)}"
    
    def _create_container(self) -> Tuple[bool, str]:
        """Crée le conteneur Neo4j avec la configuration par défaut"""
        try:
            logger.info(f"Création du conteneur {self.CONTAINER_NAME}...")
            
            # Commande pour créer le conteneur avec les paramètres par défaut
            cmd = [
                "docker", "run", "-d",
                "--name", self.CONTAINER_NAME,
                "-p", f"{self.BROWSER_PORT}:7474",
                "-p", f"{self.BOLT_PORT}:7687",
                "-e", f"NEO4J_AUTH={self.DEFAULT_USER}/{self.DEFAULT_PASSWORD}",
                "-e", "NEO4J_PLUGINS='[\"apoc\"]'",  # Plugin APOC pour les fonctionnalités avancées
                "-e", "NEO4J_dbms_security_procedures_unrestricted=apoc.*",
                "-e", "NEO4J_dbms_memory_heap_initial__size=512m",
                "-e", "NEO4J_dbms_memory_heap_max__size=1G",
                "--restart", "unless-stopped",
                self.DEFAULT_IMAGE
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode != 0:
                return False, f"Erreur lors de la création: {result.stderr}"
            
            logger.info("Conteneur Neo4j créé avec succès")
            return True, "Conteneur créé"
            
        except subprocess.TimeoutExpired:
            return False, "Timeout lors de la création du conteneur"
        except Exception as e:
            return False, f"Erreur inattendue: {str(e)}"
    
    def start_container(self) -> Tuple[bool, str]:
        """Démarre le conteneur Neo4j"""
        try:
            logger.info(f"Démarrage du conteneur {self.CONTAINER_NAME}...")
            
            result = subprocess.run(
                ["docker", "start", self.CONTAINER_NAME],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                return False, f"Erreur lors du démarrage: {result.stderr}"
            
            # Attendre que Neo4j soit prêt
            logger.info("Attente que Neo4j soit prêt...")
            for attempt in range(60):  # 60 secondes max (plus patient)
                time.sleep(1)
                status = self.check_status()
                if status.is_running:
                    logger.info("Neo4j est prêt !")
                    return True, "Conteneur démarré avec succès"
            
            return False, "Timeout: Neo4j n'a pas démarré dans les 60 secondes"
            
        except subprocess.TimeoutExpired:
            return False, "Timeout lors du démarrage du conteneur"
        except Exception as e:
            return False, f"Erreur inattendue: {str(e)}"
    
    def ensure_running(self) -> Tuple[bool, str]:
        """S'assure que Neo4j est en cours d'exécution"""
        status = self.check_status()
        
        if status.is_running:
            logger.info(f"Neo4j est déjà en cours d'exécution (ID: {status.container_id})")
            return True, "Neo4j déjà en cours d'exécution"
        
        # Si le conteneur existe mais n'est pas en cours d'exécution, le démarrer
        if status.container_id and not status.is_running:
            logger.info("Conteneur existant détecté, démarrage...")
            success, message = self.start_container()
            
            if success:
                self._status = self.check_status()
                return True, message
            else:
                logger.error(f"Impossible de démarrer le conteneur existant: {message}")
                return False, message
        
        # Si le conteneur n'existe pas, le créer
        if "non trouvé" in (status.error_message or ""):
            logger.info("Conteneur Neo4j non trouvé, création...")
            
            # Télécharger l'image si nécessaire
            pull_success, pull_message = self._pull_image()
            if not pull_success:
                return False, f"Impossible de télécharger l'image: {pull_message}"
            
            # Créer le conteneur
            create_success, create_message = self._create_container()
            if not create_success:
                return False, f"Impossible de créer le conteneur: {create_message}"
            
            # Démarrer le conteneur
            start_success, start_message = self.start_container()
            if start_success:
                self._status = self.check_status()
                return True, f"Conteneur créé et démarré: {start_message}"
            else:
                return False, f"Conteneur créé mais impossible de le démarrer: {start_message}"
        
        # Autres erreurs
        if status.error_message:
            logger.error(f"Erreur Neo4j: {status.error_message}")
            return False, status.error_message
        
        return False, "État Neo4j inconnu"
    
    def get_connection_info(self) -> dict:
        """Retourne les informations de connexion Neo4j"""
        return {
            "bolt_uri": f"bolt://localhost:{self.BOLT_PORT}",
            "browser_uri": f"http://localhost:{self.BROWSER_PORT}",
            "container_name": self.CONTAINER_NAME,
            "username": self.DEFAULT_USER,
            "password": self.DEFAULT_PASSWORD,
            "auth_string": f"{self.DEFAULT_USER}:{self.DEFAULT_PASSWORD}"
        }

# Instance singleton
_neo4j_manager: Optional[Neo4jManager] = None

def get_neo4j_manager() -> Neo4jManager:
    """Retourne l'instance singleton du gestionnaire Neo4j"""
    global _neo4j_manager
    if _neo4j_manager is None:
        _neo4j_manager = Neo4jManager()
    return _neo4j_manager

def ensure_neo4j_running() -> Tuple[bool, str]:
    """Fonction utilitaire pour s'assurer que Neo4j est en cours d'exécution"""
    manager = get_neo4j_manager()
    return manager.ensure_running()

def get_neo4j_credentials() -> dict:
    """Retourne les identifiants par défaut pour Neo4j"""
    manager = get_neo4j_manager()
    return {
        "username": manager.DEFAULT_USER,
        "password": manager.DEFAULT_PASSWORD
    }

def reset_neo4j_container() -> Tuple[bool, str]:
    """Supprime et recrée le conteneur Neo4j (pour les tests)"""
    manager = get_neo4j_manager()
    
    try:
        # Arrêter et supprimer le conteneur existant
        logger.info("Suppression du conteneur Neo4j existant...")
        subprocess.run(["docker", "stop", manager.CONTAINER_NAME], 
                      capture_output=True, timeout=10)
        subprocess.run(["docker", "rm", manager.CONTAINER_NAME], 
                      capture_output=True, timeout=10)
        
        # Recréer le conteneur
        return manager.ensure_running()
        
    except Exception as e:
        return False, f"Erreur lors de la réinitialisation: {str(e)}" 