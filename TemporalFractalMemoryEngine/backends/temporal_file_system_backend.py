class TemporalFileSystemBackend:
    """Mock backend pour les tests."""
    def __init__(self, base_path=None):
        self.base_path = base_path or "/tmp/temporal_mock"
        print(f"Mock TemporalFileSystemBackend initialisé: {self.base_path}")
    def save_node(self, node_id, node_data):
        print(f"Mock save_node: {node_id}")
        return True
