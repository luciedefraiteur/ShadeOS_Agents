#!/usr/bin/env python3
"""
🤖 MD Daemon Core - Prototype

Daemon intelligent pour hiérarchisation automatique des fichiers Markdown
utilisant OpenAI, MemoryEngine et le système de partitioning.

Créé par Alma, Architecte Démoniaque du Nexus Luciforme.
"""

import asyncio
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Ajout du path pour les imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from Core.Archivist.MemoryEngine.engine import MemoryEngine
except ImportError:
    # Fallback si MemoryEngine n'est pas disponible
    class MemoryEngine:
        def __init__(self):
            pass
        def create_memory(self, *args, **kwargs):
            pass
        def get_memory_node(self, *args, **kwargs):
            return None
        def find_memories_by_keyword(self, *args, **kwargs):
            return []
try:
    from Core.Archivist.MemoryEngine.EditingSession.partitioning import (
        LanguageRegistry,
        partition_file,
        PartitionResult
    )
    from Core.Archivist.MemoryEngine.EditingSession.partitioning.partition_schemas import (
        PartitionBlock,
        PartitionMethod,
        BlockType
    )
except ImportError:
    # Fallback si partitioning n'est pas disponible
    from enum import Enum
    from dataclasses import dataclass
    from typing import List, Dict, Any

    class PartitionMethod(Enum):
        AST = "ast"
        TREE_SITTER = "tree_sitter"
        REGEX = "regex"
        TEXTUAL = "textual"
        EMERGENCY = "emergency"

    class BlockType(Enum):
        SECTION = "section"
        FUNCTION = "function"
        CLASS = "class"

    @dataclass
    class PartitionBlock:
        block_name: str
        block_type: BlockType
        content: str
        metadata: Dict[str, Any]

    @dataclass
    class PartitionResult:
        success: bool
        partitions: List[PartitionBlock]
        method_used: PartitionMethod
        processing_time: float

    class LanguageRegistry:
        @staticmethod
        def get_language_for_file(file_path: str) -> str:
            return "markdown"

    def partition_file(file_path: str, content: str) -> PartitionResult:
        return PartitionResult(
            success=True,
            partitions=[PartitionBlock("full_content", BlockType.SECTION, content, {})],
            method_used=PartitionMethod.TEXTUAL,
            processing_time=0.1
        )
# Imports conditionnels pour éviter les erreurs d'import relatif
try:
    from .openai_analyzer import OpenAIAnalyzer, AIInsights
    from .contextual_md_analyzer import ContextualMDAnalyzer, ContextualAnalysis
    from .content_type_detector import ContentTypeDetector, ContentType, ContentCharacteristics
except ImportError:
    from openai_analyzer import OpenAIAnalyzer, AIInsights
    from contextual_md_analyzer import ContextualMDAnalyzer, ContextualAnalysis
    from content_type_detector import ContentTypeDetector, ContentType, ContentCharacteristics


@dataclass
class DaemonConfig:
    """Configuration du daemon."""
    
    # Budget OpenAI
    openai_budget_per_hour: float = 2.0
    openai_budget_per_day: float = 20.0
    
    # Seuils d'analyse
    min_file_size_for_ai: int = 500
    max_file_size_for_ai: int = 50000
    partition_threshold: int = 5000
    
    # Fréquence
    file_watch_debounce: float = 2.0
    hierarchy_update_interval: int = 300
    
    # Exclusions
    exclude_dirs: List[str] = None
    exclude_patterns: List[str] = None
    
    def __post_init__(self):
        if self.exclude_dirs is None:
            self.exclude_dirs = ["ShadeOS", ".git", "__pycache__", "node_modules"]
        if self.exclude_patterns is None:
            self.exclude_patterns = ["*.tmp.md", "*_backup.md", "*_test.md"]


@dataclass
class DocumentAnalysis:
    """Analyse d'un document."""
    
    file_path: str
    analysis_time: datetime
    file_size: int
    word_count: int
    basic_importance: float
    ai_analyzed: bool = False
    ai_insights: Optional[Dict] = None
    partitioned: bool = False
    partition_count: int = 0
    memory_path: str = ""
    cost: float = 0.0
    processing_time: float = 0.0


class MDFileWatcher(FileSystemEventHandler):
    """Surveillant de fichiers Markdown."""
    
    def __init__(self, daemon_core):
        self.daemon_core = daemon_core
        self.pending_files = {}  # Debouncing
        
    def on_modified(self, event):
        if not event.is_directory and event.src_path.endswith('.md'):
            self._schedule_processing(event.src_path, 'modified')
    
    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith('.md'):
            self._schedule_processing(event.src_path, 'created')
    
    def on_deleted(self, event):
        if not event.is_directory and event.src_path.endswith('.md'):
            asyncio.create_task(self.daemon_core.handle_file_deleted(event.src_path))
    
    def _schedule_processing(self, file_path: str, event_type: str):
        """Programme le traitement avec debouncing."""
        
        # Annule le traitement précédent si existe
        if file_path in self.pending_files:
            self.pending_files[file_path].cancel()
        
        # Programme nouveau traitement
        loop = asyncio.get_event_loop()
        task = loop.call_later(
            self.daemon_core.config.file_watch_debounce,
            lambda: asyncio.create_task(
                self.daemon_core.handle_file_changed(file_path, event_type)
            )
        )
        self.pending_files[file_path] = task


class MDDaemonCore:
    """Cœur du daemon de hiérarchisation intelligente."""

    def __init__(self, root_path: str = ".", config: DaemonConfig = None, force_ollama: bool = False):
        self.root_path = Path(root_path).resolve()
        self.config = config or DaemonConfig()
        self.force_ollama = force_ollama
        
        # Composants principaux
        self.memory_engine = MemoryEngine()
        self.language_registry = LanguageRegistry()
        self.openai_analyzer = OpenAIAnalyzer(
            budget_per_hour=config.openai_budget_per_hour,
            budget_per_day=config.openai_budget_per_day,
            force_ollama=self.force_ollama
        )
        self.contextual_analyzer = ContextualMDAnalyzer(
            memory_engine=self.memory_engine,
            max_recursive_depth=3,
            force_ollama=self.force_ollama
        )
        self.content_detector = ContentTypeDetector()
        
        # État du daemon
        self.running = False
        self.observer = None
        self.file_watcher = MDFileWatcher(self)
        
        # Statistiques
        self.stats = {
            'files_processed': 0,
            'ai_analyses': 0,
            'partitioned_files': 0,
            'total_cost': 0.0,
            'start_time': None
        }
        
        # Namespace mémoire
        self.md_namespace = "/documents/markdown"
        
    async def start_daemon(self):
        """Lance le daemon en mode surveillance continue."""
        
        print("🤖 Starting MD Daemon Core...")
        print(f"📁 Watching: {self.root_path}")
        print(f"🚫 Excluding: {', '.join(self.config.exclude_dirs)}")
        if self.force_ollama:
            print("🦙 Force Ollama mode: Using local AI only")
        
        self.running = True
        self.stats['start_time'] = datetime.now()
        
        # Scan initial
        await self._initial_scan()
        
        # Démarrage de la surveillance
        self._start_file_watching()
        
        # Boucle principale
        try:
            while self.running:
                await asyncio.sleep(self.config.hierarchy_update_interval)
                await self._update_hierarchy()
                
        except KeyboardInterrupt:
            print("\n🛑 Daemon stopped by user")
        finally:
            await self.stop_daemon()
    
    async def stop_daemon(self):
        """Arrête le daemon proprement."""
        
        print("🛑 Stopping MD Daemon...")
        self.running = False
        
        if self.observer:
            self.observer.stop()
            self.observer.join()
        
        # Statistiques finales
        await self._print_final_stats()
    
    def _start_file_watching(self):
        """Démarre la surveillance des fichiers."""
        
        self.observer = Observer()
        self.observer.schedule(
            self.file_watcher, 
            str(self.root_path), 
            recursive=True
        )
        self.observer.start()
        print("👁️ File watching started")
    
    async def _initial_scan(self):
        """Scan initial de tous les fichiers MD."""
        
        print("🔍 Initial scan of Markdown files...")
        
        md_files = []
        for md_file in self.root_path.rglob("*.md"):
            if md_file.is_file() and not self._is_excluded(md_file):
                md_files.append(md_file)
        
        print(f"📄 Found {len(md_files)} Markdown files")
        
        # Traitement par batch pour éviter la surcharge
        batch_size = 10
        for i in range(0, len(md_files), batch_size):
            batch = md_files[i:i + batch_size]
            
            tasks = [
                self.handle_file_changed(str(file_path), 'initial_scan')
                for file_path in batch
            ]
            
            await asyncio.gather(*tasks, return_exceptions=True)
            
            print(f"📊 Processed {min(i + batch_size, len(md_files))}/{len(md_files)} files")
            
            # Pause entre les batches
            await asyncio.sleep(1)
    
    async def handle_file_changed(self, file_path: str, event_type: str):
        """Traite un changement de fichier."""
        
        try:
            if not self._should_process_file(file_path):
                return
            
            print(f"📝 Processing: {Path(file_path).name} ({event_type})")
            
            # Lecture du contenu
            content = await self._read_file_safely(file_path)
            if not content:
                return
            
            # Détection du type de contenu
            content_characteristics = self.content_detector.detect_content_type(file_path, content)
            print(f"🔍 Content type: {content_characteristics.content_type.value} (confidence: {content_characteristics.confidence_score:.2f})")

            # Analyse de base
            analysis = await self._analyze_file_basic(file_path, content)

            # Décision d'analyse avancée (adaptée au type)
            if self._should_use_advanced_analysis(content, analysis, content_characteristics):
                await self._analyze_file_advanced(file_path, content, analysis, content_characteristics)

            # Décision d'analyse contextuelle
            if self._should_use_contextual_analysis(content, analysis):
                await self._analyze_file_contextual(file_path, content, analysis)
            
            # Stockage en mémoire
            await self._store_analysis(analysis)
            
            self.stats['files_processed'] += 1
            
        except Exception as e:
            print(f"❌ Error processing {file_path}: {e}")
    
    async def handle_file_deleted(self, file_path: str):
        """Traite la suppression d'un fichier."""
        
        print(f"🗑️ File deleted: {Path(file_path).name}")
        
        # Suppression de la mémoire
        memory_path = self._file_path_to_memory_path(file_path)
        try:
            self.memory_engine.forget_memory(memory_path)
            print(f"🧹 Cleaned from memory: {memory_path}")
        except Exception as e:
            print(f"⚠️ Error cleaning memory: {e}")
    
    async def _analyze_file_basic(self, file_path: str, content: str) -> DocumentAnalysis:
        """Analyse de base d'un fichier."""
        
        word_count = len(content.split())
        basic_importance = self._calculate_basic_importance(file_path, content)
        
        return DocumentAnalysis(
            file_path=file_path,
            analysis_time=datetime.now(),
            file_size=len(content),
            word_count=word_count,
            basic_importance=basic_importance,
            memory_path=self._file_path_to_memory_path(file_path)
        )
    
    async def _analyze_file_advanced(self, file_path: str, content: str, analysis: DocumentAnalysis):
        """Analyse avancée avec partitioning et OpenAI."""

        # Partitioning si nécessaire
        if len(content) > self.config.partition_threshold:
            await self._partition_file(file_path, content, analysis)

        # Analyse OpenAI réelle
        try:
            ai_insights = await self.openai_analyzer.analyze_content(content, file_path)
            analysis.ai_analyzed = True
            analysis.ai_insights = asdict(ai_insights)
            analysis.cost = ai_insights.estimated_cost

            print(f"🤖 AI Analysis: {ai_insights.domain} | Score: {ai_insights.importance_score:.1f} | Cost: ${ai_insights.estimated_cost:.4f}")

            self.stats['ai_analyses'] += 1
            self.stats['total_cost'] += analysis.cost

        except Exception as e:
            print(f"⚠️ AI analysis failed for {file_path}: {e}")
            # Fallback vers simulation
            ai_insights = await self._simulate_ai_analysis(content)
            analysis.ai_analyzed = False
            analysis.ai_insights = ai_insights
            analysis.cost = 0.0

    async def _analyze_file_contextual(self, file_path: str, content: str, analysis: DocumentAnalysis):
        """Analyse contextuelle avec MemoryEngine."""

        try:
            print(f"🧠 Starting contextual analysis for {Path(file_path).name}")

            # Analyse contextuelle complète
            contextual_analysis = await self.contextual_analyzer.analyze_with_context(file_path, content)

            # Enrichissement de l'analyse de base
            analysis.ai_insights = asdict(contextual_analysis.ai_insights)
            analysis.cost += contextual_analysis.ai_insights.estimated_cost

            # Métadonnées contextuelles
            contextual_metadata = {
                'contextual_memories_count': len(contextual_analysis.contextual_memories),
                'related_documents_count': len(contextual_analysis.related_documents),
                'memory_injections_count': len(contextual_analysis.memory_injections),
                'context_score': contextual_analysis.context_score,
                'recursive_depth': contextual_analysis.recursive_depth,
                'memory_path': contextual_analysis.memory_path
            }

            # Stockage des métadonnées contextuelles
            await self._store_contextual_metadata(file_path, contextual_metadata)

            print(f"🧠 Contextual analysis completed: Score {contextual_analysis.context_score:.1f}")

        except Exception as e:
            print(f"⚠️ Contextual analysis failed for {file_path}: {e}")

    async def _store_contextual_metadata(self, file_path: str, contextual_metadata: Dict):
        """Stocke les métadonnées contextuelles."""

        try:
            base_path = self._file_path_to_memory_path(file_path)
            metadata_path = f"{base_path}/contextual_metadata"

            self.memory_engine.create_memory(
                path=metadata_path,
                content=json.dumps(contextual_metadata, indent=2),
                summary=f"Contextual metadata for {Path(file_path).name}",
                keywords=['contextual_metadata', 'daemon_analysis', 'memory_engine'],
                strata='cognitive'
            )

        except Exception as e:
            print(f"⚠️ Error storing contextual metadata: {e}")
    
    async def _partition_file(self, file_path: str, content: str, analysis: DocumentAnalysis):
        """Partitionne un fichier avec le système de partitioning complet."""

        try:
            # Utilisation du système de partitioning avec fallbacks
            # Force le langage 'markdown' pour les fichiers .md
            language = 'markdown' if file_path.endswith('.md') else None
            result = partition_file(file_path, content, language)

            if result.success and result.partitions:
                analysis.partitioned = True
                analysis.partition_count = len(result.partitions)

                # Informations détaillées sur le partitioning
                strategy_used = result.strategy_used.value if result.strategy_used else "unknown"
                print(f"🔧 Partitioned into {len(result.partitions)} blocks using {strategy_used}")

                # Analyse des types de blocs
                block_types = {}
                for partition in result.partitions:
                    block_type = partition.block_type.value
                    block_types[block_type] = block_types.get(block_type, 0) + 1

                if block_types:
                    types_str = ", ".join(f"{k}:{v}" for k, v in block_types.items())
                    print(f"📊 Block types: {types_str}")

                self.stats['partitioned_files'] += 1

                # Stockage des partitions en mémoire avec métadonnées enrichies
                await self._store_partitions_enhanced(file_path, result)
            else:
                print(f"⚠️ Partitioning returned no blocks for {file_path}")

        except Exception as e:
            print(f"❌ Partitioning failed for {file_path}: {e}")
    
    async def _simulate_ai_analysis(self, content: str) -> Dict:
        """Simulation d'analyse OpenAI (à remplacer par vraie intégration)."""
        
        # Simulation basique
        await asyncio.sleep(0.1)  # Simule le temps d'API
        
        return {
            'classification': {
                'type': 'documentation',
                'level': 'intermediate',
                'domain': 'technical'
            },
            'semantic_tags': ['markdown', 'documentation', 'technical'],
            'summary': content[:200] + "..." if len(content) > 200 else content,
            'importance_score': min(100, len(content) / 100),
            'estimated_cost': len(content) * 0.00001  # Simulation coût
        }
    
    async def _store_analysis(self, analysis: DocumentAnalysis):
        """Stocke l'analyse dans MemoryEngine."""
        
        try:
            content = json.dumps(asdict(analysis), default=str, indent=2)
            
            self.memory_engine.create_memory(
                path=analysis.memory_path,
                content=content,
                summary=f"Analysis of {Path(analysis.file_path).name}",
                keywords=['markdown', 'document', 'analysis'],
                strata='cognitive'
            )
            
        except Exception as e:
            print(f"⚠️ Error storing analysis: {e}")
    
    async def _store_partitions_enhanced(self, file_path: str, partition_result: PartitionResult):
        """Stocke les partitions avec métadonnées enrichies."""

        base_path = self._file_path_to_memory_path(file_path)

        # Stockage du résultat global
        try:
            result_path = f"{base_path}/partition_result"
            result_metadata = {
                'strategy_used': partition_result.strategy_used.value if partition_result.strategy_used else 'unknown',
                'total_partitions': len(partition_result.partitions),
                'processing_time': partition_result.processing_time,
                'file_type': partition_result.file_type,
                'success': partition_result.success,
                'errors': partition_result.errors,
                'warnings': partition_result.warnings
            }

            self.memory_engine.create_memory(
                path=result_path,
                content=json.dumps(result_metadata, indent=2),
                summary=f"Partition result for {Path(file_path).name}",
                keywords=['partition_result', 'metadata', partition_result.strategy_used.value if partition_result.strategy_used else 'unknown'],
                strata='cognitive'
            )
        except Exception as e:
            print(f"⚠️ Error storing partition result: {e}")

        # Stockage des partitions individuelles
        for i, partition in enumerate(partition_result.partitions):
            try:
                partition_path = f"{base_path}/partition_{i:03d}"

                # Métadonnées enrichies de la partition
                partition_metadata = {
                    'block_name': partition.block_name,
                    'block_type': partition.block_type.value,
                    'partition_method': partition.partition_method.value if partition.partition_method else 'unknown',
                    'token_count': partition.token_count,
                    'complexity_score': getattr(partition, 'complexity_score', 0.0),
                    'location': {
                        'start_line': partition.location.start_line,
                        'end_line': partition.location.end_line,
                        'start_char': partition.location.start_char,
                        'end_char': partition.location.end_char
                    } if partition.location else None,
                    'metadata': partition.metadata or {}
                }

                # Contenu avec métadonnées
                full_content = {
                    'content': partition.content,
                    'metadata': partition_metadata
                }

                # Keywords enrichis
                keywords = [
                    'partition',
                    'markdown',
                    partition.block_type.value,
                    partition.partition_method.value if partition.partition_method else 'unknown'
                ]

                # Ajout de keywords depuis les métadonnées
                if partition.metadata:
                    for key, value in partition.metadata.items():
                        if isinstance(value, str) and len(value) < 20:
                            keywords.append(f"{key}:{value}")

                self.memory_engine.create_memory(
                    path=partition_path,
                    content=json.dumps(full_content, indent=2),
                    summary=f"Partition {i:03d}: {partition.block_name} ({partition.block_type.value})",
                    keywords=keywords[:10],  # Limite à 10 keywords
                    strata='cognitive'
                )

            except Exception as e:
                print(f"⚠️ Error storing partition {i}: {e}")
    
    async def _update_hierarchy(self):
        """Met à jour la hiérarchie globale."""
        
        print("📊 Updating global hierarchy...")
        
        # Génération d'un rapport de statut
        await self._generate_status_report()
    
    async def _generate_status_report(self):
        """Génère un rapport de statut du daemon."""
        
        uptime = datetime.now() - self.stats['start_time']

        # Récupération des statistiques OpenAI
        cost_summary = self.openai_analyzer.get_cost_summary()

        report = f"""# 🤖 MD Daemon Status Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Uptime:** {uptime}

## 📊 Processing Statistics
- **Files processed:** {self.stats['files_processed']}
- **AI analyses:** {self.stats['ai_analyses']}
- **Partitioned files:** {self.stats['partitioned_files']}
- **Total processing cost:** ${self.stats['total_cost']:.4f}

## 💰 OpenAI Cost Management
- **Daily usage:** ${cost_summary['daily_cost']:.4f} / ${cost_summary['daily_budget']:.2f}
- **Hourly usage:** ${cost_summary['hourly_cost']:.4f} / ${cost_summary['hourly_budget']:.2f}
- **Daily remaining:** ${cost_summary['daily_remaining']:.4f}
- **Hourly remaining:** ${cost_summary['hourly_remaining']:.4f}
- **Total requests:** {cost_summary['requests_count']}
- **Total tokens:** {cost_summary['tokens_used']}

## 🎯 Configuration
- **Root path:** {self.root_path}
- **OpenAI budget/hour:** ${self.config.openai_budget_per_hour}
- **OpenAI budget/day:** ${self.config.openai_budget_per_day}
- **Partition threshold:** {self.config.partition_threshold} chars
- **Excluded directories:** {', '.join(self.config.exclude_dirs)}

## 🤖 OpenAI Status
- **Available:** {'✅ Yes' if self.openai_analyzer.openai_available else '❌ No (simulation mode)'}
- **Client:** {'✅ Initialized' if self.openai_analyzer.client else '❌ Not available'}

*Report generated by MD Daemon Core with OpenAI integration*
"""
        
        # Sauvegarde du rapport
        report_path = self.root_path / "MD_DAEMON_STATUS.md"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
    
    def _should_process_file(self, file_path: str) -> bool:
        """Détermine si un fichier doit être traité."""
        
        path = Path(file_path)
        
        # Vérifications de base
        if not path.exists() or not path.is_file():
            return False
        
        if not path.name.endswith('.md'):
            return False
        
        return not self._is_excluded(path)
    
    def _is_excluded(self, file_path: Path) -> bool:
        """Vérifie si un fichier est exclu."""
        
        # Répertoires exclus
        for exclude_dir in self.config.exclude_dirs:
            if exclude_dir in file_path.parts:
                return True
        
        # Patterns exclus
        for pattern in self.config.exclude_patterns:
            if file_path.match(pattern):
                return True
        
        return False
    
    def _should_use_advanced_analysis(self, content: str, analysis: DocumentAnalysis) -> bool:
        """Décide si l'analyse avancée est nécessaire."""

        return (
            len(content) >= self.config.min_file_size_for_ai and
            len(content) <= self.config.max_file_size_for_ai and
            analysis.basic_importance > 30  # Seuil d'importance
        )

    def _should_use_contextual_analysis(self, content: str, analysis: DocumentAnalysis) -> bool:
        """Décide si l'analyse contextuelle est nécessaire."""

        return (
            len(content) >= 200 and  # Contenu minimum pour contexte
            analysis.basic_importance > 50 and  # Importance élevée
            len(content.split()) > 50  # Au moins 50 mots
        )
    
    def _calculate_basic_importance(self, file_path: str, content: str) -> float:
        """Calcule un score d'importance basique."""
        
        score = 0.0
        
        # Taille du contenu
        word_count = len(content.split())
        if word_count > 1000:
            score += 30
        elif word_count > 500:
            score += 20
        elif word_count > 100:
            score += 10
        
        # Mots-clés dans le nom
        name_lower = Path(file_path).name.lower()
        important_keywords = ['plan', 'architecture', 'design', 'implementation']
        for keyword in important_keywords:
            if keyword in name_lower:
                score += 15
        
        # Profondeur dans l'arborescence (moins profond = plus important)
        depth = len(Path(file_path).relative_to(self.root_path).parts)
        score += max(0, 20 - (depth * 5))
        
        return min(100.0, score)
    
    def _file_path_to_memory_path(self, file_path: str) -> str:
        """Convertit un chemin de fichier en chemin mémoire."""
        
        rel_path = Path(file_path).relative_to(self.root_path)
        memory_key = str(rel_path).replace('/', '_').replace('.md', '')
        return f"{self.md_namespace}/{memory_key}"
    
    async def _read_file_safely(self, file_path: str) -> Optional[str]:
        """Lit un fichier de manière sécurisée."""
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            try:
                with open(file_path, 'r', encoding='latin-1') as f:
                    return f.read()
            except Exception as e:
                print(f"⚠️ Error reading {file_path}: {e}")
                return None
        except Exception as e:
            print(f"⚠️ Error reading {file_path}: {e}")
            return None
    
    async def _print_final_stats(self):
        """Affiche les statistiques finales."""
        
        uptime = datetime.now() - self.stats['start_time']
        
        print("\n📊 Final Statistics:")
        print(f"  ⏱️ Uptime: {uptime}")
        print(f"  📄 Files processed: {self.stats['files_processed']}")
        print(f"  🤖 AI analyses: {self.stats['ai_analyses']}")
        print(f"  🔧 Partitioned files: {self.stats['partitioned_files']}")
        print(f"  💰 Total cost: ${self.stats['total_cost']:.4f}")


async def main():
    """Fonction principale du daemon."""
    
    import argparse
    
    parser = argparse.ArgumentParser(description="🤖 MD Daemon Core - Intelligent Markdown Hierarchy")
    parser.add_argument("--root", "-r", default=".", help="Root directory to watch")
    parser.add_argument("--budget-hour", type=float, default=2.0, help="OpenAI budget per hour")
    parser.add_argument("--exclude", nargs="*", default=None, help="Directories to exclude")
    parser.add_argument("--force-ollama", action="store_true", help="Force Ollama usage (skip OpenAI)")
    
    args = parser.parse_args()
    
    # Configuration
    config = DaemonConfig()
    config.openai_budget_per_hour = args.budget_hour
    if args.exclude:
        config.exclude_dirs = args.exclude
    
    # Lancement du daemon
    daemon = MDDaemonCore(args.root, config, force_ollama=args.force_ollama)
    await daemon.start_daemon()


if __name__ == "__main__":
    asyncio.run(main())
