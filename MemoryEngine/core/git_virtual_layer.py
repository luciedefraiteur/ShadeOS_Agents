#!/usr/bin/env python3
"""
⛧ Git Virtual Layer - Couche Virtuelle Git ⛧

Couche d'abstraction pour utiliser Git comme système de recherche virtuel.
Intègre l'historique Git avec le MemoryEngine pour recherche intelligente.
"""

import asyncio
import os
import re
import json
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass

from .engine import MemoryEngine
from .meta_path_adapter import MetaPathAdapter


@dataclass
class GitCommit:
    """Représentation d'un commit Git"""
    hash: str
    author: str
    date: str
    message: str
    files_changed: List[str]
    insertions: int
    deletions: int
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit le commit en dictionnaire pour sérialisation JSON"""
        return {
            "hash": self.hash,
            "author": self.author,
            "date": self.date,
            "message": self.message,
            "files_changed": self.files_changed,
            "insertions": self.insertions,
            "deletions": self.deletions,
            "metadata": self.metadata
        }


@dataclass
class GitSearchResult:
    """Résultat de recherche Git"""
    query: str
    commits: List[GitCommit]
    files_affected: List[str]
    patterns_found: List[str]
    search_method: str
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit le résultat en dictionnaire pour sérialisation JSON"""
        return {
            "query": self.query,
            "commits": [commit.to_dict() for commit in self.commits],
            "files_affected": self.files_affected,
            "patterns_found": self.patterns_found,
            "search_method": self.search_method,
            "metadata": self.metadata
        }


class GitVirtualLayer:
    """Couche virtuelle Git pour recherche intelligente"""
    
    def __init__(self, memory_engine: MemoryEngine, workspace_path: str = "."):
        self.memory_engine = memory_engine
        self.workspace_path = Path(workspace_path).resolve()
        self.git_cache = {}
        
    async def search_git_history(self, query: str, context: Dict[str, Any] = None) -> GitSearchResult:
        """
        Recherche intelligente dans l'historique Git
        
        Args:
            query: Requête de recherche
            context: Contexte supplémentaire
            
        Returns:
            GitSearchResult avec commits et métadonnées
        """
        context = context or {}
        
        # Détection du type de recherche Git
        search_type = await self._detect_git_search_type(query)
        
        # Exécution de la recherche selon le type
        if search_type == "commit_message":
            commits = await self._search_commit_messages(query)
        elif search_type == "file_history":
            commits = await self._search_file_history(query)
        elif search_type == "author_pattern":
            commits = await self._search_author_pattern(query)
        elif search_type == "code_changes":
            commits = await self._search_code_changes(query)
        else:
            commits = await self._search_general(query)
        
        # Analyse des patterns et métadonnées
        patterns = await self._analyze_commit_patterns(commits)
        files_affected = await self._extract_files_affected(commits)
        
        return GitSearchResult(
            query=query,
            commits=commits,
            files_affected=files_affected,
            patterns_found=patterns,
            search_method=search_type,
            metadata={
                "total_commits": len(commits),
                "time_range": await self._get_time_range(commits),
                "authors": await self._extract_authors(commits),
                "context": context
            }
        )
    
    async def _detect_git_search_type(self, query: str) -> str:
        """Détection simple du type de recherche Git"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ["commit", "message", "log"]):
            return "commit_message"
        elif any(word in query_lower for word in ["file", "fichier", "path"]):
            return "file_history"
        elif any(word in query_lower for word in ["author", "qui", "who", "lucie", "alma"]):
            return "author_pattern"
        elif any(word in query_lower for word in ["code", "change", "modification", "bug"]):
            return "code_changes"
        else:
            return "general"
    
    async def _search_commit_messages(self, query: str) -> List[GitCommit]:
        """Recherche dans les messages de commit"""
        commits = []
        
        try:
            # Commande git log avec recherche dans les messages
            cmd = [
                "git", "log", "--grep", query, "--pretty=format:%H|%an|%ad|%s",
                "--date=short", "--all"
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(self.workspace_path)
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                for line in stdout.decode().splitlines():
                    if line.strip():
                        commit = await self._parse_commit_line(line)
                        if commit:
                            commits.append(commit)
                            
        except Exception as e:
            print(f"⚠️ Erreur recherche commit messages: {e}")
        
        return commits
    
    async def _search_file_history(self, query: str) -> List[GitCommit]:
        """Recherche dans l'historique des fichiers"""
        commits = []
        
        try:
            # Extraction du nom de fichier depuis la requête
            file_pattern = self._extract_file_pattern(query)
            
            if file_pattern:
                cmd = [
                    "git", "log", "--follow", "--pretty=format:%H|%an|%ad|%s",
                    "--date=short", "--", file_pattern
                ]
                
                process = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    cwd=str(self.workspace_path)
                )
                
                stdout, stderr = await process.communicate()
                
                if process.returncode == 0:
                    for line in stdout.decode().splitlines():
                        if line.strip():
                            commit = await self._parse_commit_line(line)
                            if commit:
                                commits.append(commit)
                                
        except Exception as e:
            print(f"⚠️ Erreur recherche file history: {e}")
        
        return commits
    
    async def _search_author_pattern(self, query: str) -> List[GitCommit]:
        """Recherche par pattern d'auteur"""
        commits = []
        
        try:
            # Extraction du nom d'auteur depuis la requête
            author_pattern = self._extract_author_pattern(query)
            
            if author_pattern:
                cmd = [
                    "git", "log", "--author", author_pattern, "--pretty=format:%H|%an|%ad|%s",
                    "--date=short", "--all"
                ]
                
                process = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    cwd=str(self.workspace_path)
                )
                
                stdout, stderr = await process.communicate()
                
                if process.returncode == 0:
                    for line in stdout.decode().splitlines():
                        if line.strip():
                            commit = await self._parse_commit_line(line)
                            if commit:
                                commits.append(commit)
                                
        except Exception as e:
            print(f"⚠️ Erreur recherche author pattern: {e}")
        
        return commits
    
    async def _search_code_changes(self, query: str) -> List[GitCommit]:
        """Recherche dans les changements de code"""
        commits = []
        
        try:
            # Recherche dans les diffs
            cmd = [
                "git", "log", "-S", query, "--pretty=format:%H|%an|%ad|%s",
                "--date=short", "--all"
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(self.workspace_path)
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                for line in stdout.decode().splitlines():
                    if line.strip():
                        commit = await self._parse_commit_line(line)
                        if commit:
                            commits.append(commit)
                            
        except Exception as e:
            print(f"⚠️ Erreur recherche code changes: {e}")
        
        return commits
    
    async def _search_general(self, query: str) -> List[GitCommit]:
        """Recherche générale dans Git"""
        commits = []
        
        try:
            # Recherche combinée
            cmd = [
                "git", "log", "--grep", query, "--author", query,
                "--pretty=format:%H|%an|%ad|%s", "--date=short", "--all"
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(self.workspace_path)
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                for line in stdout.decode().splitlines():
                    if line.strip():
                        commit = await self._parse_commit_line(line)
                        if commit:
                            commits.append(commit)
                            
        except Exception as e:
            print(f"⚠️ Erreur recherche générale: {e}")
        
        return commits
    
    async def _parse_commit_line(self, line: str) -> Optional[GitCommit]:
        """Parse une ligne de commit Git"""
        try:
            parts = line.split('|')
            if len(parts) >= 4:
                commit_hash = parts[0]
                author = parts[1]
                date = parts[2]
                message = parts[3]
                
                # Récupération des fichiers modifiés
                files_changed = await self._get_files_changed(commit_hash)
                
                # Récupération des statistiques
                stats = await self._get_commit_stats(commit_hash)
                
                return GitCommit(
                    hash=commit_hash,
                    author=author,
                    date=date,
                    message=message,
                    files_changed=files_changed,
                    insertions=stats.get('insertions', 0),
                    deletions=stats.get('deletions', 0),
                    metadata={
                        'short_hash': commit_hash[:8],
                        'timestamp': date
                    }
                )
        except Exception as e:
            print(f"⚠️ Erreur parsing commit line: {e}")
        
        return None
    
    async def _get_files_changed(self, commit_hash: str) -> List[str]:
        """Récupère les fichiers modifiés dans un commit"""
        files = []
        
        try:
            cmd = ["git", "show", "--name-only", "--pretty=format:", commit_hash]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(self.workspace_path)
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                for line in stdout.decode().splitlines():
                    if line.strip() and not line.startswith('commit'):
                        files.append(line.strip())
                        
        except Exception as e:
            print(f"⚠️ Erreur récupération fichiers: {e}")
        
        return files
    
    async def _get_commit_stats(self, commit_hash: str) -> Dict[str, int]:
        """Récupère les statistiques d'un commit"""
        stats = {'insertions': 0, 'deletions': 0}
        
        try:
            cmd = ["git", "show", "--stat", "--pretty=format:", commit_hash]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(self.workspace_path)
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                output = stdout.decode()
                # Parse des statistiques (format: "X files changed, Y insertions(+), Z deletions(-)")
                stat_match = re.search(r'(\d+) files? changed(?:, (\d+) insertions?\(\+\))?(?:, (\d+) deletions?\(-\))?', output)
                if stat_match:
                    stats['files_changed'] = int(stat_match.group(1))
                    if stat_match.group(2):
                        stats['insertions'] = int(stat_match.group(2))
                    if stat_match.group(3):
                        stats['deletions'] = int(stat_match.group(3))
                        
        except Exception as e:
            print(f"⚠️ Erreur récupération stats: {e}")
        
        return stats
    
    def _extract_file_pattern(self, query: str) -> Optional[str]:
        """Extrait un pattern de fichier depuis la requête"""
        # Patterns simples pour détecter des noms de fichiers
        patterns = [
            r'(\w+\.py)',  # Fichiers Python
            r'(\w+\.md)',  # Fichiers Markdown
            r'(\w+\.json)',  # Fichiers JSON
            r'(\w+\.txt)',  # Fichiers texte
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    def _extract_author_pattern(self, query: str) -> Optional[str]:
        """Extrait un pattern d'auteur depuis la requête"""
        # Noms connus
        known_authors = ['lucie', 'alma', 'lucie defraiteur']
        
        query_lower = query.lower()
        for author in known_authors:
            if author in query_lower:
                return author
        
        return None
    
    async def _analyze_commit_patterns(self, commits: List[GitCommit]) -> List[str]:
        """Analyse les patterns dans les commits"""
        patterns = []
        
        if not commits:
            return patterns
        
        # Patterns temporels
        dates = [commit.date for commit in commits]
        if len(dates) > 1:
            patterns.append(f"Time span: {min(dates)} to {max(dates)}")
        
        # Patterns d'auteurs
        authors = set(commit.author for commit in commits)
        if authors:
            patterns.append(f"Authors: {', '.join(authors)}")
        
        # Patterns de fichiers
        all_files = set()
        for commit in commits:
            all_files.update(commit.files_changed)
        
        if all_files:
            file_types = {}
            for file in all_files:
                ext = Path(file).suffix
                file_types[ext] = file_types.get(ext, 0) + 1
            
            patterns.append(f"File types: {dict(file_types)}")
        
        return patterns
    
    async def _extract_files_affected(self, commits: List[GitCommit]) -> List[str]:
        """Extrait tous les fichiers affectés"""
        files = set()
        for commit in commits:
            files.update(commit.files_changed)
        return list(files)
    
    async def _get_time_range(self, commits: List[GitCommit]) -> Dict[str, str]:
        """Calcule la plage temporelle des commits"""
        if not commits:
            return {"start": "", "end": ""}
        
        dates = [commit.date for commit in commits]
        return {
            "start": min(dates),
            "end": max(dates)
        }
    
    async def _extract_authors(self, commits: List[GitCommit]) -> List[str]:
        """Extrait tous les auteurs uniques"""
        authors = set(commit.author for commit in commits)
        return list(authors)
    
    async def find_related_commits(self, file_path: str) -> List[GitCommit]:
        """Trouve les commits liés à un fichier spécifique"""
        return await self._search_file_history(f"file:{file_path}")
    
    async def analyze_development_patterns(self, time_range: str = "auto") -> Dict[str, Any]:
        """Analyse les patterns de développement sur une période intelligente"""
        try:
            # Détection intelligente de la période d'activité
            if time_range == "auto":
                # Récupération de tous les commits pour analyser la vraie période
                cmd_all = [
                    "git", "log", "--pretty=format:%ad", "--date=short", "--all"
                ]
                
                process = await asyncio.create_subprocess_exec(
                    *cmd_all,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    cwd=str(self.workspace_path)
                )
                
                stdout, stderr = await process.communicate()
                
                if process.returncode == 0:
                    dates = [line.strip() for line in stdout.decode().splitlines() if line.strip()]
                    if dates:
                        # Calcul de la vraie période d'activité
                        start_date = min(dates)
                        end_date = max(dates)
                        actual_days = (datetime.strptime(end_date, "%Y-%m-%d") - datetime.strptime(start_date, "%Y-%m-%d")).days + 1
                        
                        # Ajustement intelligent de la période
                        if actual_days <= 7:
                            time_range = f"{actual_days} days"
                        elif actual_days <= 30:
                            time_range = f"{actual_days} days"
                        else:
                            time_range = f"{actual_days} days"
                    else:
                        time_range = "unknown"
                        start_date = "2020-01-01"
                else:
                    time_range = "1 month"
                    start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
            else:
                # Période spécifiée manuellement
                if time_range == "1 month":
                    start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
                elif time_range == "1 week":
                    start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
                else:
                    start_date = "2020-01-01"  # Par défaut
            
            # Récupération des commits sur la période
            cmd = [
                "git", "log", f"--since={start_date}",
                "--pretty=format:%H|%an|%ad|%s", "--date=short", "--all"
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(self.workspace_path)
            )
            
            stdout, stderr = await process.communicate()
            
            commits = []
            if process.returncode == 0:
                for line in stdout.decode().splitlines():
                    if line.strip():
                        commit = await self._parse_commit_line(line)
                        if commit:
                            commits.append(commit)
            
            # Analyse des patterns
            actual_time_range = await self._get_time_range(commits)
            
            # Calcul de métadonnées intelligentes
            commits_per_day = len(commits) / max(1, actual_days) if 'actual_days' in locals() else 0
            intensity = "🔥 Intense" if commits_per_day > 10 else "⚡ Actif" if commits_per_day > 5 else "📝 Modéré"
            
            return {
                "period": time_range,
                "actual_days": actual_days if 'actual_days' in locals() else "unknown",
                "total_commits": len(commits),
                "commits_per_day": round(commits_per_day, 1),
                "development_intensity": intensity,
                "authors": await self._extract_authors(commits),
                "files_affected": await self._extract_files_affected(commits),
                "patterns": await self._analyze_commit_patterns(commits),
                "time_range": actual_time_range,
                "insights": {
                    "activity_span": f"{actual_days if 'actual_days' in locals() else 'unknown'} days",
                    "commit_frequency": f"{round(commits_per_day, 1)} commits/day",
                    "project_phase": "🚀 Active Development" if commits_per_day > 5 else "🔧 Maintenance"
                }
            }
            
        except Exception as e:
            print(f"⚠️ Erreur analyse patterns: {e}")
            return {}
    
    async def virtual_git_search(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Recherche virtuelle unifiée Git + MemoryEngine
        
        Args:
            query: Requête de recherche
            context: Contexte supplémentaire
            
        Returns:
            Résultats combinés Git + MemoryEngine
        """
        context = context or {}
        
        # Recherche Git
        git_result = await self.search_git_history(query, context)
        
        # Recherche MemoryEngine
        memory_results = self.memory_engine.find_memories_by_keyword(query)
        
        # Combinaison des résultats
        return {
            "query": query,
            "git_results": {
                "commits": len(git_result.commits),
                "files_affected": len(git_result.files_affected),
                "patterns": git_result.patterns_found,
                "search_method": git_result.search_method
            },
            "memory_results": {
                "memories_found": len(memory_results),
                "paths": memory_results
            },
            "combined_insights": {
                "total_results": len(git_result.commits) + len(memory_results),
                "has_git_history": len(git_result.commits) > 0,
                "has_memory_context": len(memory_results) > 0
            },
            "context": context,
            "timestamp": datetime.now().isoformat()
        } 