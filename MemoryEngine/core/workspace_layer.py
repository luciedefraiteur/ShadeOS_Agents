#!/usr/bin/env python3
"""
⛧ Workspace Layer - Couche d'Abstraction Workspace ⛧

Couche haut niveau pour la gestion workspace avec recherche intelligente.
Choisit automatiquement la meilleure méthode de recherche (grep, fractal, temporal, mixed).
"""

import asyncio
import os
import re
import subprocess
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
from datetime import datetime

from Core.LLMProviders import LLMProvider
from .engine import MemoryEngine
from .fractal_search_engine import FractalSearchEngine
from .meta_path_adapter import MetaPathAdapter, UnifiedResultFormatter


class WorkspaceLayer:
    """Couche d'abstraction pour la gestion workspace avec recherche intelligente"""
    
    def __init__(self, memory_engine: MemoryEngine, llm_provider: LLMProvider, workspace_path: str = "."):
        self.memory_engine = memory_engine
        self.llm_provider = llm_provider
        self.workspace_path = Path(workspace_path).resolve()
        self.search_engine = FractalSearchEngine(memory_engine, llm_provider)
        
        # Cache pour les patterns de code
        self.code_patterns_cache = {}
        
    async def intelligent_search(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Recherche intelligente qui choisit automatiquement la meilleure méthode
        
        Args:
            query: Requête utilisateur
            context: Contexte supplémentaire (projet, type de fichier, etc.)
            
        Returns:
            Résultats avec métadonnées sur la méthode utilisée
        """
        context = context or {}
        
        # 1. Choix intelligent de la méthode
        method = await self._choose_search_method(query, context)
        
        # 2. Exécution selon la méthode
        results = await self._execute_search_method(method, query, context)
        
        # 3. Formatage et enrichissement
        formatted_results = await self._format_and_enrich_results(results, method, query)
        
        return {
            "query": query,
            "method_used": method,
            "results": formatted_results,
            "context": context,
            "timestamp": datetime.now().isoformat()
        }
    
    async def _choose_search_method(self, query: str, context: Dict[str, Any]) -> str:
        """
        Appel LLM simple pour choisir la méthode de recherche
        """
        prompt = f"""
Query: "{query}"
Context: {context}

Choose the best search method:
- "grep" (exact patterns, code search, file content)
- "fractal" (conceptual relationships, abstract concepts)
- "temporal" (time-based, history, development flow)
- "mixed" (combine multiple methods)

Answer with just the method name.
"""
        
        try:
            response = await self.llm_provider.generate(prompt, max_tokens=10)
            method = response.strip().lower()
            
            # Validation de la réponse
            valid_methods = ["grep", "fractal", "temporal", "mixed"]
            if method in valid_methods:
                return method
            else:
                print(f"⚠️ Méthode LLM invalide '{method}', fallback 'mixed'")
                return "mixed"
                
        except Exception as e:
            print(f"⚠️ Erreur choix méthode LLM: {e}, fallback 'mixed'")
            return "mixed"
    
    async def _execute_search_method(self, method: str, query: str, context: Dict[str, Any]) -> List[Any]:
        """Exécute la méthode de recherche choisie"""
        
        if method == "grep":
            return await self._grep_search(query, context)
        elif method == "fractal":
            return await self.search_engine.search_fractal_only(query)
        elif method == "temporal":
            return await self.search_engine.search_temporal_only(query)
        elif method == "mixed":
            search_result = await self.search_engine.search(query)
            return search_result.combined_results
        else:
            print(f"⚠️ Méthode inconnue: {method}, fallback mixed")
            search_result = await self.search_engine.search(query)
            return search_result.combined_results
    
    async def _grep_search(self, query: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Recherche grep intelligente dans le workspace
        """
        results = []
        
        try:
            # Construction de la commande grep
            grep_cmd = ["grep", "-r", "-n", "--include=*.py", "--include=*.md", "--include=*.txt"]
            
            # Ajout de patterns d'exclusion si nécessaire
            if context.get("exclude_patterns"):
                for pattern in context["exclude_patterns"]:
                    grep_cmd.extend(["--exclude", pattern])
            
            grep_cmd.extend([query, str(self.workspace_path)])
            
            # Exécution de grep
            process = await asyncio.create_subprocess_exec(
                *grep_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                # Parsing des résultats
                for line in stdout.decode().splitlines():
                    if line.strip():
                        result = self._parse_grep_line(line)
                        if result:
                            results.append(result)
            else:
                print(f"⚠️ Grep error: {stderr.decode()}")
                
        except Exception as e:
            print(f"⚠️ Erreur grep search: {e}")
        
        return results
    
    def _parse_grep_line(self, line: str) -> Optional[Dict[str, Any]]:
        """Parse une ligne de résultat grep"""
        try:
            # Format: file:line:content
            parts = line.split(':', 2)
            if len(parts) >= 3:
                file_path = parts[0]
                line_number = int(parts[1])
                content = parts[2]
                
                # Chemin relatif
                relative_path = os.path.relpath(file_path, str(self.workspace_path))
                
                return {
                    "type": "grep_result",
                    "file_path": relative_path,
                    "line_number": line_number,
                    "content": content.strip(),
                    "full_path": file_path
                }
        except Exception as e:
            print(f"⚠️ Erreur parsing grep line: {e}")
        
        return None
    
    async def _format_and_enrich_results(self, results: List[Any], method: str, query: str) -> List[Dict[str, Any]]:
        """Formate et enrichit les résultats"""
        formatted = []
        
        for result in results:
            if isinstance(result, dict) and result.get("type") == "grep_result":
                # Résultat grep déjà formaté
                formatted.append(result)
            else:
                # Résultat fractal/temporel à formater
                formatted_result = {
                    "type": f"{method}_result",
                    "content": str(result),
                    "query": query,
                    "method": method
                }
                
                # Enrichissement avec métadonnées si possible
                if hasattr(result, 'metadata'):
                    formatted_result["metadata"] = result.metadata
                if hasattr(result, 'strata'):
                    formatted_result["strata"] = result.strata
                
                formatted.append(formatted_result)
        
        return formatted
    
    async def create_workspace_memory(self, file_path: str, content: str, context: Dict[str, Any] = None) -> bool:
        """
        Crée un nœud mémoire avec contexte workspace enrichi
        """
        context = context or {}
        
        # Analyse du fichier
        file_info = await self._analyze_file(file_path, content)
        
        # Métadonnées workspace enrichies
        workspace_metadata = {
            "workspace_path": str(self.workspace_path),
            "file_type": file_info["file_type"],
            "file_size": file_info["file_size"],
            "code_patterns": file_info["code_patterns"],
            "git_info": await self._get_git_info(file_path),
            **context
        }
        
        # Création du nœud mémoire
        success = self.memory_engine.create_memory(
            path=f"workspace/{file_path}",
            content=content,
            summary=file_info["summary"],
            keywords=file_info["keywords"],
            strata=context.get("strata", "cognitive")
        )
        
        # Les métadonnées workspace sont automatiquement ajoutées par le backend
        # lors de la création du FractalMemoryNode
        
        return success
    
    async def _analyze_file(self, file_path: str, content: str) -> Dict[str, Any]:
        """Analyse un fichier pour extraire des métadonnées"""
        file_info = {
            "file_type": Path(file_path).suffix,
            "file_size": len(content),
            "code_patterns": [],
            "summary": content[:200] + "..." if len(content) > 200 else content,
            "keywords": []
        }
        
        # Analyse des patterns de code pour les fichiers Python
        if file_path.endswith('.py'):
            file_info["code_patterns"] = await self._extract_code_patterns(content)
            file_info["keywords"] = await self._extract_keywords(content)
        
        return file_info
    
    async def _extract_code_patterns(self, content: str) -> List[str]:
        """Extrait les patterns de code (fonctions, classes, imports)"""
        patterns = []
        
        # Patterns simples avec regex
        patterns.extend(re.findall(r'def\s+(\w+)', content))  # Fonctions
        patterns.extend(re.findall(r'class\s+(\w+)', content))  # Classes
        patterns.extend(re.findall(r'import\s+(\w+)', content))  # Imports
        patterns.extend(re.findall(r'from\s+(\w+)', content))  # From imports
        
        return list(set(patterns))  # Suppression des doublons
    
    async def _extract_keywords(self, content: str) -> List[str]:
        """Extrait les mots-clés du contenu"""
        # Mots-clés basiques (peut être amélioré avec LLM)
        keywords = []
        
        # Patterns de mots-clés
        keyword_patterns = [
            r'\b\w{4,}\b',  # Mots de 4+ caractères
        ]
        
        for pattern in keyword_patterns:
            matches = re.findall(pattern, content)
            keywords.extend(matches)
        
        # Filtrage et limitation
        keywords = [kw.lower() for kw in keywords if kw.isalpha()]
        keywords = list(set(keywords))[:20]  # Limite à 20 mots-clés
        
        return keywords
    
    async def _get_git_info(self, file_path: str) -> Dict[str, Any]:
        """Récupère les informations git pour un fichier"""
        git_info = {}
        
        try:
            # Statut git
            process = await asyncio.create_subprocess_exec(
                "git", "status", "--porcelain", file_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(self.workspace_path)
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0 and stdout:
                git_info["status"] = stdout.decode().strip()
            
            # Branche actuelle
            process = await asyncio.create_subprocess_exec(
                "git", "branch", "--show-current",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(self.workspace_path)
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                git_info["branch"] = stdout.decode().strip()
                
        except Exception as e:
            print(f"⚠️ Erreur git info: {e}")
        
        return git_info
    
    async def analyze_workspace_structure(self) -> Dict[str, Any]:
        """Analyse la structure complète du workspace"""
        structure = {
            "workspace_path": str(self.workspace_path),
            "files": [],
            "directories": [],
            "file_types": {},
            "total_files": 0,
            "total_size": 0
        }
        
        try:
            for root, dirs, files in os.walk(str(self.workspace_path)):
                # Exclusion des dossiers cachés et node_modules
                dirs[:] = [d for d in dirs if not d.startswith('.') and d != 'node_modules']
                
                for file in files:
                    if not file.startswith('.'):
                        file_path = os.path.join(root, file)
                        relative_path = os.path.relpath(file_path, str(self.workspace_path))
                        
                        try:
                            file_size = os.path.getsize(file_path)
                            file_ext = Path(file).suffix
                            
                            structure["files"].append({
                                "path": relative_path,
                                "size": file_size,
                                "extension": file_ext
                            })
                            
                            structure["total_files"] += 1
                            structure["total_size"] += file_size
                            
                            # Comptage par type de fichier
                            if file_ext not in structure["file_types"]:
                                structure["file_types"][file_ext] = 0
                            structure["file_types"][file_ext] += 1
                            
                        except Exception as e:
                            print(f"⚠️ Erreur analyse fichier {file_path}: {e}")
                            
        except Exception as e:
            print(f"⚠️ Erreur analyse workspace: {e}")
        
        return structure
    
    async def track_development_flow(self, action: str, context: Dict[str, Any] = None) -> bool:
        """
        Suit le flux de développement pour mémoire temporelle
        """
        context = context or {}
        
        # Création d'un nœud mémoire pour l'action
        memory_content = f"Action: {action}\nContext: {context}\nTimestamp: {datetime.now().isoformat()}"
        
        success = self.memory_engine.create_memory(
            path=f"development/flow/{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            content=memory_content,
            summary=f"Development action: {action}",
            keywords=["development", "flow", "action"] + context.get("keywords", []),
            strata="cognitive"
        )
        
        return success 