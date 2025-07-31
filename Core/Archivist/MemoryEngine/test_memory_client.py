import unittest
import os
import shutil
import json

import sys
# Ajoute le répertoire racine du projet au PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from Core.Archivist.MemoryEngine.engine import MemoryEngine

class TestMemoryClient(unittest.TestCase):

    def setUp(self):
        self.test_base_path = os.path.abspath('./.test_memory_client_root')
        self.engine = MemoryEngine(base_path=self.test_base_path)
        # S'assure que le répertoire de test est propre avant chaque test
        if os.path.exists(self.test_base_path):
            shutil.rmtree(self.test_base_path)
        os.makedirs(self.engine.backend.memory_root, exist_ok=True)

    def tearDown(self):
        # Nettoie après chaque test
        if os.path.exists(self.test_base_path):
            shutil.rmtree(self.test_base_path)

    def test_client_create_and_get_memory(self):
        path = "my_first_memory"
        content = "Ceci est le contenu de ma première mémoire."
        summary = "Première mémoire de test."
        keywords = ["test", "client", "premier"]
        
        success = self.engine.create_memory(path, content, summary, keywords)
        self.assertTrue(success)
        
        retrieved_memory = self.engine.get_memory_node(path)
        self.assertIsNotNone(retrieved_memory)
        self.assertEqual(retrieved_memory["descriptor"], content)
        self.assertEqual(retrieved_memory["summary"], summary)
        self.assertEqual(retrieved_memory["keywords"], keywords)

    def test_client_linked_memories(self):
        self.engine.create_memory("linked_target_1", "target content 1", "target summary 1", ["target"])
        self.engine.create_memory("linked_target_2", "target content 2", "target summary 2", ["target"])

        path = "memory_with_links"
        content = "Cette mémoire a des liens."
        summary = "Mémoire avec liens."
        keywords = ["liens", "test"]
        links = ["linked_target_1", "linked_target_2"]

        success = self.engine.create_memory(path, content, summary, keywords, links=links)
        self.assertTrue(success)

        retrieved_memory = self.engine.get_memory_node(path)
        self.assertEqual(len(retrieved_memory["linked_memories"]), 2)
        linked_paths = [l["path"] for l in retrieved_memory["linked_memories"]]
        self.assertIn("linked_target_1", linked_paths)
        self.assertIn("linked_target_2", linked_paths)

    def test_client_find_by_keyword(self):
        self.engine.create_memory("node_a", "content a", "summary a", ["tag1", "tag2"])
        self.engine.create_memory("node_b", "content b", "summary b", ["tag2", "tag3"])
        self.engine.create_memory("node_c", "content c", "summary c", ["tag1", "tag4"])

        results = self.engine.find_memories_by_keyword("tag2")
        self.assertIn("node_a", results)
        self.assertIn("node_b", results)
        self.assertNotIn("node_c", results)
        self.assertEqual(len(results), 2)

    def test_client_list_children(self):
        self.engine.create_memory("parent_node", "parent content", "parent summary", ["parent"])
        self.engine.create_memory("parent_node/child_a", "child a content", "child a summary", ["child"])
        self.engine.create_memory("parent_node/child_b", "child b content", "child b summary", ["child"])

        children = self.engine.list_children("parent_node")
        self.assertEqual(len(children), 2)
        child_names = [c["path"] for c in children]
        self.assertIn("child_a", child_names)
        self.assertIn("child_b", child_names)

if __name__ == '__main__':
    unittest.main()
