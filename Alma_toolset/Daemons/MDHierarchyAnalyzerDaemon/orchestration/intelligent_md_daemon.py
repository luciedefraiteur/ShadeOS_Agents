#!/usr/bin/env python3
"""
🎭 Intelligent MD Daemon

MD Daemon avec orchestration intelligente basée sur des prompts.
L'IA génère des instructions d'orchestration pour optimiser l'analyse.

Créé par Alma, Architecte Démoniaque du Nexus Luciforme.
"""

import asyncio
import argparse
import sys
import os
from pathlib import Path
from typing import Dict, Any

# Ajout du path pour les imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Imports conditionnels
try:
    from ..adapters.message_bus import MessageBus
    from ..adapters.protocol_adapters import ContentDetectorAdapter, AIAnalyzerAdapter, MemoryEngineAdapter
    from .intelligent_orchestrator import IntelligentOrchestrator
    from ..core.content_type_detector import ContentTypeDetector
    from ..core.openai_analyzer import OpenAIAnalyzer
    from Core.Archivist.MemoryEngine.engine import MemoryEngine
except ImportError:
    try:
        from message_bus import MessageBus
        from protocol_adapters import ContentDetectorAdapter, AIAnalyzerAdapter, MemoryEngineAdapter
        from intelligent_orchestrator import IntelligentOrchestrator
        from content_type_detector import ContentTypeDetector
        from openai_analyzer import OpenAIAnalyzer
        from Core.Archivist.MemoryEngine.engine import MemoryEngine
    except ImportError:
        # Fallback complet
        class MessageBus:
            def __init__(self): pass
            async def start(self): pass
            async def stop(self): pass
        class ContentDetectorAdapter:
            def __init__(self, *args): pass
        class AIAnalyzerAdapter:
            def __init__(self, *args): pass
        class MemoryEngineAdapter:
            def __init__(self, *args): pass
        class IntelligentOrchestrator:
            def __init__(self, *args): pass
        class ContentTypeDetector:
            def __init__(self): pass
        class OpenAIAnalyzer:
            def __init__(self, *args, **kwargs): pass
        class MemoryEngine:
            def __init__(self): pass


class IntelligentMDDaemon:
    """MD Daemon avec orchestration intelligente."""
    
    def __init__(self, root_path: str = ".", force_ollama: bool = False, 
                 budget_hour: float = 2.0, exclude_dirs: list = None):
        self.root_path = Path(root_path).resolve()
        self.force_ollama = force_ollama
        self.budget_hour = budget_hour
        self.exclude_dirs = exclude_dirs or ["ShadeOS", ".git", "__pycache__", "node_modules"]
        
        # Statistiques
        self.files_processed = 0
        self.total_processing_time = 0.0
        self.orchestration_stats = {}
        
        print("🎭 Intelligent MD Daemon initializing...")
        print(f"📁 Root path: {self.root_path}")
        print(f"🦙 Force Ollama: {self.force_ollama}")
        print(f"💰 Budget/hour: ${self.budget_hour}")
        print(f"🚫 Excluded: {', '.join(self.exclude_dirs)}")
    
    async def initialize(self):
        """Initialise tous les composants."""
        
        print("🎭 Initializing components...")
        
        # 1. Message Bus
        self.message_bus = MessageBus()
        await self.message_bus.start()
        
        # 2. Core Components
        self.content_detector = ContentTypeDetector()
        self.ai_analyzer = OpenAIAnalyzer(
            budget_per_hour=self.budget_hour,
            force_ollama=self.force_ollama
        )
        self.memory_engine = MemoryEngine()
        
        # 3. Protocol Adapters
        self.content_adapter = ContentDetectorAdapter(self.content_detector, self.message_bus)
        self.ai_adapter = AIAnalyzerAdapter(self.ai_analyzer, self.message_bus)
        self.memory_adapter = MemoryEngineAdapter(self.memory_engine, self.message_bus)
        
        # 4. Intelligent Orchestrator
        self.orchestrator = IntelligentOrchestrator(self.message_bus, self.ai_analyzer)
        
        print("🎭 All components initialized successfully")
    
    async def scan_and_process(self):
        """Scan et traitement intelligent des fichiers MD."""
        
        print("🎭 Starting intelligent scan and processing...")
        
        # Recherche des fichiers MD
        md_files = []
        for md_file in self.root_path.rglob("*.md"):
            if md_file.is_file() and not self._is_excluded(md_file):
                md_files.append(md_file)
        
        print(f"📄 Found {len(md_files)} Markdown files")
        
        if not md_files:
            print("📄 No Markdown files found to process")
            return
        
        # Traitement par batch
        batch_size = 5
        for i in range(0, len(md_files), batch_size):
            batch = md_files[i:i + batch_size]
            
            print(f"\n🎭 Processing batch {i//batch_size + 1}/{(len(md_files)-1)//batch_size + 1}")
            
            # Traitement parallèle du batch
            tasks = [
                self.process_file_intelligent(str(file_path))
                for file_path in batch
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Analyse des résultats
            for j, result in enumerate(results):
                if isinstance(result, Exception):
                    print(f"❌ Error processing {batch[j].name}: {result}")
                else:
                    print(f"✅ Processed {batch[j].name}: {result.get('status', 'unknown')}")
            
            # Délai entre batches
            if i + batch_size < len(md_files):
                await asyncio.sleep(1.0)
        
        # Rapport final
        await self._generate_final_report()
    
    async def process_file_intelligent(self, file_path: str) -> Dict[str, Any]:
        """Traitement intelligent d'un fichier via orchestration."""
        
        try:
            # Lecture du fichier
            content = await self._read_file_safely(file_path)
            if not content:
                return {"status": "skipped", "reason": "empty_or_unreadable"}
            
            print(f"🎭 Intelligent processing: {Path(file_path).name}")
            
            # Orchestration intelligente
            orchestration_result = await self.orchestrator.orchestrate_analysis(file_path, content)
            
            # Mise à jour des statistiques
            self.files_processed += 1
            self.total_processing_time += orchestration_result.processing_time
            
            # Enregistrement des stats d'orchestration
            self._update_orchestration_stats(orchestration_result)
            
            return {
                "status": "completed",
                "orchestration_success": orchestration_result.orchestration_success,
                "components_executed": orchestration_result.total_components_executed,
                "processing_time": orchestration_result.processing_time,
                "enhancement_applied": orchestration_result.enhancement_applied
            }
            
        except Exception as e:
            print(f"❌ Error in intelligent processing of {file_path}: {e}")
            return {"status": "error", "error": str(e)}
    
    async def _read_file_safely(self, file_path: str) -> str:
        """Lecture sécurisée d'un fichier."""
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Validation basique
            if len(content.strip()) < 10:
                return ""
            
            return content
            
        except Exception as e:
            print(f"⚠️ Error reading {file_path}: {e}")
            return ""
    
    def _is_excluded(self, file_path: Path) -> bool:
        """Vérifie si un fichier doit être exclu."""
        
        path_str = str(file_path)
        
        for exclude_dir in self.exclude_dirs:
            if exclude_dir in path_str:
                return True
        
        return False
    
    def _update_orchestration_stats(self, result):
        """Met à jour les statistiques d'orchestration."""
        
        if result.orchestration_success:
            self.orchestration_stats["successful"] = self.orchestration_stats.get("successful", 0) + 1
        else:
            self.orchestration_stats["failed"] = self.orchestration_stats.get("failed", 0) + 1
        
        self.orchestration_stats["total_components"] = self.orchestration_stats.get("total_components", 0) + result.total_components_executed
        
        if result.enhancement_applied:
            self.orchestration_stats["enhanced"] = self.orchestration_stats.get("enhanced", 0) + 1
    
    async def _generate_final_report(self):
        """Génère le rapport final."""
        
        print("\n" + "="*60)
        print("🎭 INTELLIGENT MD DAEMON - FINAL REPORT")
        print("="*60)
        
        # Statistiques générales
        print(f"\n📊 Processing Statistics:")
        print(f"  📄 Files processed: {self.files_processed}")
        print(f"  ⏱️ Total processing time: {self.total_processing_time:.2f}s")
        if self.files_processed > 0:
            print(f"  📈 Average time per file: {self.total_processing_time / self.files_processed:.2f}s")
        
        # Statistiques d'orchestration
        print(f"\n🎭 Orchestration Statistics:")
        total_orchestrations = self.orchestration_stats.get("successful", 0) + self.orchestration_stats.get("failed", 0)
        if total_orchestrations > 0:
            success_rate = self.orchestration_stats.get("successful", 0) / total_orchestrations
            print(f"  ✅ Success rate: {success_rate:.2%}")
            print(f"  🔧 Total components executed: {self.orchestration_stats.get('total_components', 0)}")
            print(f"  📈 Average components per file: {self.orchestration_stats.get('total_components', 0) / total_orchestrations:.1f}")
            print(f"  🧠 Enhanced analyses: {self.orchestration_stats.get('enhanced', 0)}")
        
        # Statistiques des composants
        print(f"\n📡 Component Health:")
        try:
            bus_status = self.message_bus.get_health_status()
            print(f"  📡 Message Bus: {bus_status['status']}")
            print(f"  📨 Total messages: {bus_status['total_messages']}")
            print(f"  ❌ Total errors: {bus_status['total_errors']}")
            
            if bus_status['total_messages'] > 0:
                error_rate = bus_status['total_errors'] / bus_status['total_messages']
                print(f"  📊 Error rate: {error_rate:.2%}")
        except Exception as e:
            print(f"  ⚠️ Error getting bus status: {e}")
        
        # Statistiques de l'orchestrateur
        try:
            orchestrator_stats = self.orchestrator.get_orchestration_stats()
            print(f"\n🎭 Orchestrator Performance:")
            print(f"  🎯 Total orchestrations: {orchestrator_stats.get('total_orchestrations', 0)}")
            print(f"  ✅ Success rate: {orchestrator_stats.get('success_rate', 0):.2%}")
            print(f"  ⏱️ Average processing time: {orchestrator_stats.get('average_processing_time', 0):.2f}s")
            print(f"  🧠 Enhancement usage: {orchestrator_stats.get('enhancement_usage_rate', 0):.2%}")
        except Exception as e:
            print(f"  ⚠️ Error getting orchestrator stats: {e}")
        
        # Coûts AI
        try:
            cost_summary = self.ai_analyzer.get_cost_summary()
            print(f"\n💰 AI Cost Summary:")
            print(f"  💵 Daily cost: ${cost_summary['daily_cost']:.4f} / ${cost_summary['daily_budget']:.2f}")
            print(f"  💵 Hourly cost: ${cost_summary['hourly_cost']:.4f} / ${cost_summary['hourly_budget']:.2f}")
            print(f"  📊 Requests made: {cost_summary['requests_made']}")
        except Exception as e:
            print(f"  ⚠️ Error getting cost summary: {e}")
        
        print("\n" + "="*60)
        print("🎭 Intelligent processing completed!")
        print("="*60)
    
    async def shutdown(self):
        """Arrêt propre du daemon."""
        
        print("\n🎭 Shutting down Intelligent MD Daemon...")
        
        try:
            await self.message_bus.stop()
            print("📡 Message Bus stopped")
        except Exception as e:
            print(f"⚠️ Error stopping message bus: {e}")
        
        print("🎭 Shutdown complete")


async def main():
    """Point d'entrée principal."""
    
    parser = argparse.ArgumentParser(description="Intelligent MD Daemon with AI Orchestration")
    parser.add_argument("--root", "-r", default=".", help="Root directory to scan")
    parser.add_argument("--force-ollama", action="store_true", help="Force Ollama usage (skip OpenAI)")
    parser.add_argument("--budget-hour", type=float, default=2.0, help="OpenAI budget per hour")
    parser.add_argument("--exclude", nargs="*", default=None, help="Directories to exclude")
    
    args = parser.parse_args()
    
    # Configuration des exclusions
    exclude_dirs = args.exclude or ["ShadeOS", ".git", "__pycache__", "node_modules"]
    
    # Création et lancement du daemon
    daemon = IntelligentMDDaemon(
        root_path=args.root,
        force_ollama=args.force_ollama,
        budget_hour=args.budget_hour,
        exclude_dirs=exclude_dirs
    )
    
    try:
        # Initialisation
        await daemon.initialize()
        
        # Traitement
        await daemon.scan_and_process()
        
    except KeyboardInterrupt:
        print("\n🎭 Interrupted by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
    finally:
        # Arrêt propre
        await daemon.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
