from .storage_backends import FileSystemBackend

try:
    from .neo4j_backend import Neo4jBackend
    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False

__all__ = ['FileSystemBackend', 'Neo4jBackend', 'NEO4J_AVAILABLE'] 