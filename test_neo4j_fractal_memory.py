#!/usr/bin/env python3
"""
⛧ Test Neo4j Fractal Memory Implementation ⛧
Architecte Démoniaque du Nexus Luciforme

Tests the Neo4j backend for Fractal Memory with Strata and Respiration.

Author: Alma (via Lucie Defraiteur)
"""

import sys
import os

# Ajoute le répertoire racine du projet au PYTHONPATH
sys.path.insert(0, os.path.abspath('.'))

def test_neo4j_connection():
    """Test basic Neo4j connection."""
    print("⛧ Testing Neo4j connection...")
    
    try:
        from neo4j import GraphDatabase
        driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))
        
        with driver.session() as session:
            result = session.run("RETURN 'Hello Neo4j!' as message")
            record = result.single()
            print(f"✓ Neo4j connection successful: {record['message']}")
        
        driver.close()
        return True
        
    except Exception as e:
        print(f"✗ Neo4j connection failed: {e}")
        return False

def test_memory_engine_auto_detection():
    """Test MemoryEngine auto-detection of Neo4j."""
    print("\n⛧ Testing MemoryEngine auto-detection...")
    
    try:
        from Core.Archivist.MemoryEngine.engine import MemoryEngine
        
        # Should auto-detect Neo4j
        engine = MemoryEngine(backend_type="auto")
        print(f"✓ MemoryEngine initialized with backend: {engine.backend_type}")
        
        # Test basic functionality
        engine.create_memory(
            path="test/hello_world",
            content="This is a test memory in the fractal system.",
            summary="Test memory for Neo4j backend",
            keywords=["test", "hello", "world"],
            strata="somatic"
        )
        print("✓ Memory created successfully")
        
        # Read it back
        node = engine.get_memory_node("test/hello_world")
        print(f"✓ Memory retrieved: {node.summary}")
        print(f"✓ Strata: {node.strata} {node.get_strata_symbol()}")
        
        engine.close()
        return True
        
    except Exception as e:
        print(f"✗ MemoryEngine test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_fractal_memory_features():
    """Test advanced fractal memory features."""
    print("\n⛧ Testing Fractal Memory features...")
    
    try:
        from Core.Archivist.MemoryEngine.engine import MemoryEngine
        
        engine = MemoryEngine(backend_type="neo4j")
        
        # Create memories in different strata
        print("  Creating Somatic memory...")
        engine.create_memory(
            path="bugs/login_error_2024",
            content="User reported login error: 'Invalid credentials' when using correct password. Error occurs on Chrome 120.0.6099.109. Stack trace shows authentication service timeout.",
            summary="Login error with authentication service timeout",
            keywords=["bug", "login", "authentication", "timeout", "chrome"],
            strata="somatic"
        )
        
        print("  Creating Cognitive memory...")
        engine.create_memory(
            path="analysis/authentication_patterns",
            content="Analysis of recent authentication issues reveals pattern: timeouts occur during peak hours (12-14h, 18-20h). Load balancer may be overwhelmed. Recommend implementing connection pooling and circuit breaker pattern.",
            summary="Authentication timeout pattern analysis and recommendations",
            keywords=["analysis", "authentication", "patterns", "load", "recommendations"],
            strata="cognitive",
            immanence_links=["bugs/login_error_2024"]  # Links down to concrete bug
        )
        
        print("  Creating Metaphysical memory...")
        engine.create_memory(
            path="principles/resilient_architecture",
            content="Core principle: Systems must gracefully degrade under load. Every service should implement: 1) Circuit breakers for external dependencies, 2) Exponential backoff for retries, 3) Bulkhead isolation for critical paths, 4) Observability for rapid diagnosis.",
            summary="Resilient architecture design principles",
            keywords=["principles", "resilience", "architecture", "design", "reliability"],
            strata="metaphysical",
            immanence_links=["analysis/authentication_patterns"]  # Links down to analysis
        )
        
        # Test strata queries
        print("  Testing strata queries...")
        somatic_memories = engine.find_by_strata("somatic")
        cognitive_memories = engine.find_by_strata("cognitive")
        metaphysical_memories = engine.find_by_strata("metaphysical")
        
        print(f"✓ Found {len(somatic_memories)} somatic memories")
        print(f"✓ Found {len(cognitive_memories)} cognitive memories")
        print(f"✓ Found {len(metaphysical_memories)} metaphysical memories")
        
        # Test transcendence path
        print("  Testing transcendence traversal...")
        transcendence_path = engine.traverse_transcendence_path("bugs/login_error_2024")
        print(f"✓ Transcendence path length: {len(transcendence_path)}")
        
        # Test immanence path
        print("  Testing immanence traversal...")
        immanence_path = engine.traverse_immanence_path("principles/resilient_architecture")
        print(f"✓ Immanence path length: {len(immanence_path)}")
        
        # Get statistics
        stats = engine.get_memory_statistics()
        print(f"✓ Memory statistics:")
        print(f"  - Total nodes: {stats.get('total_nodes', 0)}")
        print(f"  - Total relationships: {stats.get('total_relationships', 0)}")
        print(f"  - Somatic nodes: {stats.get('somatic_nodes', 0)}")
        print(f"  - Cognitive nodes: {stats.get('cognitive_nodes', 0)}")
        print(f"  - Metaphysical nodes: {stats.get('metaphysical_nodes', 0)}")
        
        engine.close()
        return True
        
    except Exception as e:
        print(f"✗ Fractal Memory test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test routine."""
    print("⛧ Neo4j Fractal Memory Test Suite")
    print("⛧" + "═" * 50)
    
    # Test 1: Basic Neo4j connection
    if not test_neo4j_connection():
        print("\n⛧ Neo4j connection failed. Make sure Neo4j is running.")
        return False
    
    # Test 2: MemoryEngine auto-detection
    if not test_memory_engine_auto_detection():
        print("\n⛧ MemoryEngine auto-detection failed.")
        return False
    
    # Test 3: Advanced fractal features
    if not test_fractal_memory_features():
        print("\n⛧ Fractal Memory features test failed.")
        return False
    
    print("\n⛧" + "═" * 50)
    print("⛧ ALL TESTS PASSED! 🎭✨")
    print("⛧ Neo4j Fractal Memory is working perfectly!")
    print("⛧ Access Neo4j Browser at: http://localhost:7474")
    print("⛧ Username: neo4j, Password: password")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
