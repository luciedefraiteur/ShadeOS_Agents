#!/usr/bin/env python3
"""
⛧ Neo4j Setup and Configuration for Fractal Memory ⛧
Architecte Démoniaque du Nexus Luciforme

Sets up Neo4j for the Fractal Memory system with proper configuration.

Author: Alma (via Lucie Defraiteur)
"""

import os
import sys
import subprocess
import platform
from pathlib import Path


class Neo4jSetup:
    """
    Handles Neo4j installation and configuration for Fractal Memory.
    """
    
    def __init__(self):
        self.system = platform.system().lower()
        self.neo4j_home = None
        self.neo4j_data = Path.home() / ".neo4j" / "data"
        
    def check_python_driver(self):
        """Check if Neo4j Python driver is installed."""
        try:
            import neo4j
            print("✓ Neo4j Python driver is installed")
            return True
        except ImportError:
            print("✗ Neo4j Python driver not found")
            return False
    
    def install_python_driver(self):
        """Install Neo4j Python driver."""
        print("⛧ Installing Neo4j Python driver...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "neo4j"], check=True)
            print("✓ Neo4j Python driver installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to install Neo4j Python driver: {e}")
            return False
    
    def check_neo4j_server(self):
        """Check if Neo4j server is running."""
        try:
            from neo4j import GraphDatabase
            driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))
            with driver.session() as session:
                result = session.run("RETURN 1")
                result.single()
            driver.close()
            print("✓ Neo4j server is running and accessible")
            return True
        except Exception as e:
            print(f"✗ Neo4j server not accessible: {e}")
            return False
    
    def get_installation_instructions(self):
        """Get platform-specific installation instructions."""
        instructions = {
            "linux": """
⛧ Neo4j Installation Instructions for Linux:

1. Install Neo4j Desktop (Recommended):
   - Download from: https://neo4j.com/download/
   - Or use package manager:
     
   Ubuntu/Debian:
   wget -O - https://debian.neo4j.com/neotechnology.gpg.key | sudo apt-key add -
   echo 'deb https://debian.neo4j.com stable 4.4' | sudo tee /etc/apt/sources.list.d/neo4j.list
   sudo apt update
   sudo apt install neo4j

2. Start Neo4j:
   sudo systemctl start neo4j
   sudo systemctl enable neo4j

3. Access Neo4j Browser:
   http://localhost:7474
   Default credentials: neo4j/neo4j (change on first login)

4. Set password to 'password' for ShadeOS compatibility
""",
            "darwin": """
⛧ Neo4j Installation Instructions for macOS:

1. Install via Homebrew (Recommended):
   brew install neo4j

2. Or download Neo4j Desktop:
   https://neo4j.com/download/

3. Start Neo4j:
   neo4j start

4. Access Neo4j Browser:
   http://localhost:7474
   Default credentials: neo4j/neo4j (change on first login)

5. Set password to 'password' for ShadeOS compatibility
""",
            "windows": """
⛧ Neo4j Installation Instructions for Windows:

1. Download Neo4j Desktop:
   https://neo4j.com/download/

2. Install and create a new database

3. Set password to 'password' for ShadeOS compatibility

4. Start the database

5. Access Neo4j Browser:
   http://localhost:7474
"""
        }
        
        return instructions.get(self.system, instructions["linux"])
    
    def create_sample_data(self):
        """Create sample fractal memory data for testing."""
        print("⛧ Creating sample Fractal Memory data...")
        
        try:
            from .MemoryEngine.engine import MemoryEngine
            
            # Initialize with Neo4j backend
            engine = MemoryEngine(backend_type="neo4j")
            
            # Create sample memories across different strata
            
            # Somatic (concrete data)
            engine.create_memory(
                path="bugs/login_error_2024",
                content="User reported login error: 'Invalid credentials' when using correct password. Error occurs on Chrome 120.0.6099.109. Stack trace shows authentication service timeout.",
                summary="Login error with authentication service timeout",
                keywords=["bug", "login", "authentication", "timeout", "chrome"],
                strata="somatic"
            )
            
            # Cognitive (analysis)
            engine.create_memory(
                path="analysis/authentication_patterns",
                content="Analysis of recent authentication issues reveals pattern: timeouts occur during peak hours (12-14h, 18-20h). Load balancer may be overwhelmed. Recommend implementing connection pooling and circuit breaker pattern.",
                summary="Authentication timeout pattern analysis and recommendations",
                keywords=["analysis", "authentication", "patterns", "load", "recommendations"],
                strata="cognitive",
                immanence_links=["bugs/login_error_2024"]  # Links down to concrete bug
            )
            
            # Metaphysical (principles)
            engine.create_memory(
                path="principles/resilient_architecture",
                content="Core principle: Systems must gracefully degrade under load. Every service should implement: 1) Circuit breakers for external dependencies, 2) Exponential backoff for retries, 3) Bulkhead isolation for critical paths, 4) Observability for rapid diagnosis.",
                summary="Resilient architecture design principles",
                keywords=["principles", "resilience", "architecture", "design", "reliability"],
                strata="metaphysical",
                immanence_links=["analysis/authentication_patterns"]  # Links down to analysis
            )
            
            # Create transcendence links (bottom-up)
            engine.create_memory(
                path="bugs/login_error_2024",
                content="User reported login error: 'Invalid credentials' when using correct password. Error occurs on Chrome 120.0.6099.109. Stack trace shows authentication service timeout.",
                summary="Login error with authentication service timeout",
                keywords=["bug", "login", "authentication", "timeout", "chrome"],
                strata="somatic",
                transcendence_links=["analysis/authentication_patterns"]  # Links up to analysis
            )
            
            stats = engine.get_memory_statistics()
            print(f"✓ Sample data created successfully!")
            print(f"  - Total nodes: {stats.get('total_nodes', 0)}")
            print(f"  - Somatic nodes: {stats.get('somatic_nodes', 0)}")
            print(f"  - Cognitive nodes: {stats.get('cognitive_nodes', 0)}")
            print(f"  - Metaphysical nodes: {stats.get('metaphysical_nodes', 0)}")
            
            engine.close()
            return True
            
        except Exception as e:
            print(f"✗ Failed to create sample data: {e}")
            return False
    
    def run_setup(self):
        """Run the complete setup process."""
        print("⛧ Neo4j Setup for Fractal Memory")
        print("⛧" + "═" * 50)
        
        # Check Python driver
        if not self.check_python_driver():
            if not self.install_python_driver():
                return False
        
        # Check Neo4j server
        if not self.check_neo4j_server():
            print("\n⛧ Neo4j server is not running or not configured.")
            print(self.get_installation_instructions())
            print("\n⛧ After installing and starting Neo4j, run this script again.")
            return False
        
        # Create sample data
        if not self.create_sample_data():
            return False
        
        print("\n⛧ Setup completed successfully!")
        print("⛧ You can now use the Fractal Memory system with Neo4j backend.")
        print("⛧ Access Neo4j Browser at: http://localhost:7474")
        
        return True


def main():
    """Main setup routine."""
    setup = Neo4jSetup()
    success = setup.run_setup()
    
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
