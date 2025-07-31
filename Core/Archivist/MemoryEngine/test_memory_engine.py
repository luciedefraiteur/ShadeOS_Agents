import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
import unittest
import shutil
import json
from Core.Archivist.MemoryEngine.engine import MemoryEngine
from Core.Archivist.MemoryEngine.memory_node import FractalMemoryNode

class TestMemoryEngine(unittest.TestCase):

    def setUp(self):
        self.test_base_path = os.path.abspath('./.test_memory_root')
        self.engine = MemoryEngine(base_path=self.test_base_path)
        # S'assure que le répertoire de test est propre avant chaque test
        if os.path.exists(self.test_base_path):
            shutil.rmtree(self.test_base_path)
        os.makedirs(self.engine.backend.memory_root, exist_ok=True)

    def tearDown(self):
        # Nettoie après chaque test
        if os.path.exists(self.test_base_path):
            shutil.rmtree(self.test_base_path)

    def test_create_memory(self):
        path = "test_node"
        content = "Contenu du test."
        summary = "Résumé du test."
        keywords = ["test", "mémoire"]
        
        success = self.engine.create_memory(path, content, summary, keywords)
        self.assertTrue(success)
        
        # Vérifie que le fichier a été créé
        node_path = os.path.join(self.engine.backend.memory_root, path, '.fractal_memory')
        self.assertTrue(os.path.exists(node_path))
        
        # Vérifie le contenu
        node = self.engine.backend.read(path)
        self.assertEqual(node.descriptor, content)
        self.assertEqual(node.summary, summary)
        self.assertEqual(node.keywords, keywords)

    def test_get_memory_node(self):
        path = "test_node_get"
        content = "Contenu pour get."
        summary = "Résumé pour get."
        keywords = ["get", "node"]
        self.engine.create_memory(path, content, summary, keywords)

        retrieved_node = self.engine.get_memory_node(path)
        self.assertIsNotNone(retrieved_node)
        self.assertEqual(retrieved_node["descriptor"], content)
        self.assertEqual(retrieved_node["summary"], summary)

    def test_find_memories_by_keyword(self):
        self.engine.create_memory("node1", "c1", "s1", ["a", "b"])
        self.engine.create_memory("node2", "c2", "s2", ["b", "c"])
        self.engine.create_memory("node3", "c3", "s3", ["a", "d"])

        results = self.engine.find_memories_by_keyword("b")
        self.assertIn("node1", results)
        self.assertIn("node2", results)
        self.assertNotIn("node3", results)
        self.assertEqual(len(results), 2)

    def test_list_children(self):
        self.engine.create_memory("parent", "p", "p", ["p"])
        self.engine.create_memory("parent/child1", "c1", "c1", ["c1"])
        self.engine.create_memory("parent/child2", "c2", "c2", ["c2"])

        children = self.engine.list_children("parent")
        self.assertEqual(len(children), 2)
        child_names = [c["path"] for c in children]
        self.assertIn("child1", child_names)
        self.assertIn("child2", child_names)

    def test_linked_memories(self):
        self.engine.create_memory("source", "s", "s", ["s"])
        self.engine.create_memory("target1", "t1", "t1", ["t1"])
        self.engine.create_memory("target2", "t2", "t2", ["t2"])

        self.engine.create_memory("source", "s", "s", ["s"], links=["target1", "target2"])

        source_node = self.engine.get_memory_node("source")
        self.assertEqual(len(source_node["linked_memories"]), 2)
        linked_paths = [l["path"] for l in source_node["linked_memories"]]
        self.assertIn("target1", linked_paths)
        self.assertIn("target2", linked_paths)

    def test_list_links(self):
        self.engine.create_memory("link_source", "ls", "ls", ["ls"])
        self.engine.create_memory("link_target1", "lt1", "lt1", ["lt1"])
        self.engine.create_memory("link_target2", "lt2", "lt2", ["lt2"])

        self.engine.create_memory("link_source", "ls", "ls", ["ls"], links=["link_target1", "link_target2"])

        links = self.engine.list_links("link_source")
        self.assertEqual(len(links), 2)
        linked_paths = [l["path"] for l in links]
        self.assertIn("link_target1", linked_paths)
        self.assertIn("link_target2", linked_paths)

if __name__ == '__main__':
    unittest.main()
