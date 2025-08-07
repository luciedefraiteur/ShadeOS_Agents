#!/usr/bin/env python3
"""
⛧ MemoryEngine V2 - WorkspaceTemporalLayer ⛧

Migration de WorkspaceLayer vers l'architecture temporelle universelle.
Compatibilité totale avec l'existant + dimension temporelle.
"""

import asyncio
import os
import re
import subprocess
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
from datetime import datetime

from Core.LLMProviders import LLMProvider
from .temporal_components import WorkspaceTemporalLayer as BaseWorkspaceTemporalLayer
# Import lazy pour éviter l'import circulaire
MemoryEngine = None
from .fractal_search_engine import FractalSearchEngine
from .meta_path_adapter import MetaPathAdapter, UnifiedResultFormatter


class WorkspaceTemporalLayer(BaseWorkspaceTemporalLayer):
    """Migration de WorkspaceLayer vers l'architecture temporelle universelle"""
    
    def __init__(self, memory_engine, llm_provider: LLMProvider, workspace_path: str = "."):
        # Initialisation de la base temporelle
        super().__init__(memory_engine)
        
        # Propriétés héritées de WorkspaceLayer
        self.llm_provider = llm_provider
        self.workspace_path = Path(workspace_path).resolve()
        self.search_engine = FractalSearchEngine(memory_engine, llm_provider)
        
        # Cache pour les patterns de code
        self.code_patterns_cache = {}
        
        # Évolution temporelle de l'initialisation
        self.temporal_dimension.evolve("workspace_layer_initialized", {
            "workspace_path": str(self.workspace_path),
            "llm_provider_available": llm_provider is not None,
            "search_engine_initialized": True
        })
    
    async def intelligent_search(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Recherche intelligente avec tracking temporel"""
        # Tracking temporel de l'accès
        self.access_layer("intelligent_search")
        
        context = context or {}
        
        # 1. Choix intelligent de la méthode
        method = await self._choose_search_method(query, context)
        
        # 2. Exécution selon la méthode
        results = await self._execute_search_method(method, query, context)
        
        # 3. Formatage et enrichissement
        formatted_results = await self._format_and_enrich_results(results, method, query)
        
        # Évolution temporelle de la recherche
        self.temporal_dimension.evolve("intelligent_search_executed", {
            "query": query,
            "method_used": method,
            "results_count": len(formatted_results),
            "context": context
        })
        
        # Apprentissage temporel
        self.learn_from_interaction({
            "type": "intelligent_search",
            "query": query,
            "method": method,
            "results_count": len(formatted_results),
            "context": context
        })
        
        return {
            "query": query,
            "method_used": method,
            "results": formatted_results,
            "context": context,
            "timestamp": datetime.now().isoformat(),
            "temporal_metadata": {
                "consciousness_level": self.get_consciousness_level(),
                "evolution_count": len(self.temporal_dimension.evolution_history)
            }
        }
    
    async def _choose_search_method(self, query: str, context: Dict[str, Any]) -> str:
        """Choix intelligent de la méthode avec apprentissage temporel"""
        # Si pas de provider LLM, utiliser une détection simple
        if self.llm_provider is None:
            method = self._simple_method_detection(query)
        else:
            # Sinon, utiliser le LLM
            method = await self._llm_method_choice(query, context)
        
        # Apprentissage du choix de méthode
        self.learn_from_interaction({
            "type": "method_choice",
            "query": query,
            "chosen_method": method,
            "context": context
        })
        
        return method
    
    def _simple_method_detection(self, query: str) -> str:
        """Détection simple basée sur les mots-clés"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ["grep", "search", "find", "file", "content"]):
            return "grep"
        elif any(word in query_lower for word in ["concept", "relation", "abstract", "memory"]):
            return "fractal"
        elif any(word in query_lower for word in ["time", "history", "recent", "old", "new"]):
            return "temporal"
        else:
            return "mixed"
    #note lucie, pour les methodes avec llm, il pourrait enrichir automatiquement les mots clés aussi, ou la requete elle meme je sais
    async def _llm_method_choice(self, query: str, context: Dict[str, Any]) -> str:
        """Choix de méthode via LLM"""
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
            response = await self.llm_provider.generate_response(prompt)
            method = response.content.strip().lower()
            
            # Validation de la méthode
            valid_methods = ["grep", "fractal", "temporal", "mixed"]
            if method not in valid_methods:
                method = "mixed"
            
            return method
        except Exception as e:
            # Fallback en cas d'erreur LLM
            self.temporal_dimension.evolve("llm_method_choice_error", {"error": str(e)})
            return self._simple_method_detection(query)
    
    async def _execute_search_method(self, method: str, query: str, context: Dict[str, Any]) -> List[Any]:
        """Exécution de la méthode de recherche avec tracking temporel"""
        try:
            if method == "grep":
                results = await self._grep_search(query, context)
            elif method == "fractal":
                results = await self.search_engine.fractal_search(query, context)
            elif method == "temporal":
                results = await self.memory_engine.temporal_index.search(query, context)
            elif method == "mixed":
                # Combinaison de méthodes
                grep_results = await self._grep_search(query, context)
                fractal_results = await self.search_engine.fractal_search(query, context)
                temporal_results = await self.memory_engine.temporal_index.search(query, context)
                
                results = {
                    "grep": grep_results,
                    "fractal": fractal_results,
                    "temporal": temporal_results
                }
            else:
                results = []
            
            # Évolution temporelle de l'exécution
            self.temporal_dimension.evolve("search_method_executed", {
                "method": method,
                "query": query,
                "results_count": len(results) if isinstance(results, list) else sum(len(r) for r in results.values())
            })
            
            return results
        except Exception as e:
            # Gestion d'erreur avec évolution temporelle
            self.temporal_dimension.evolve("search_method_error", {
                "method": method,
                "query": query,
                "error": str(e)
            })
            return []
    
    async def _grep_search(self, query: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Recherche grep avec tracking temporel"""
        try:
            # Construction de la commande grep
            grep_cmd = ["grep", "-r", "-n", "--color=never", query, str(self.workspace_path)]
            
            # Exécution de la commande
            process = await asyncio.create_subprocess_exec(
                *grep_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                lines = stdout.decode('utf-8').strip().split('\n')
                results = []
                
                for line in lines:
                    if line.strip():
                        parsed_result = self._parse_grep_line(line)
                        if parsed_result:
                            results.append(parsed_result)
                
                # Évolution temporelle de la recherche grep
                self.temporal_dimension.evolve("grep_search_completed", {
                    "query": query,
                    "results_count": len(results),
                    "lines_processed": len(lines)
                })
                
                return results
            else:
                # Gestion d'erreur grep
                self.temporal_dimension.evolve("grep_search_error", {
                    "query": query,
                    "error": stderr.decode('utf-8')
                })
                return []
                
        except Exception as e:
            # Gestion d'erreur générale
            self.temporal_dimension.evolve("grep_search_exception", {
                "query": query,
                "error": str(e)
            })
            return []
    
    def _parse_grep_line(self, line: str) -> Optional[Dict[str, Any]]:
        """Parse une ligne de résultat grep"""
        try:
            # Pattern: file:line:content
            match = re.match(r'^([^:]+):(\d+):(.+)$', line)
            if match:
                file_path, line_num, content = match.groups()
                return {
                    "file_path": file_path,
                    "line_number": int(line_num),
                    "content": content.strip(),
                    "full_line": line
                }
            return None
        except Exception:
            return None
    
    async def _format_and_enrich_results(self, results: List[Any], method: str, query: str) -> List[Dict[str, Any]]:
        """Formatage et enrichissement des résultats avec métadonnées temporelles"""
        formatted_results = []
        
        for result in results:
            if isinstance(result, dict):
                # Ajout de métadonnées temporelles
                result["temporal_metadata"] = {
                    "method_used": method,
                    "query": query,
                    "consciousness_level": self.get_consciousness_level(),
                    "processing_timestamp": datetime.now().isoformat()
                }
                formatted_results.append(result)
        
        # Évolution temporelle du formatage
        self.temporal_dimension.evolve("results_formatted", {
            "method": method,
            "query": query,
            "formatted_count": len(formatted_results)
        })
        
        return formatted_results
    
    async def create_workspace_memory(self, file_path: str, content: str, context: Dict[str, Any] = None) -> bool:
        """Création de mémoire workspace avec tracking temporel"""
        try:
            context = context or {}
            
            # Analyse du fichier
            analysis = await self._analyze_file(file_path, content)
            
            # Création de la mémoire
            memory_created = await self.memory_engine.create_memory(
                path=file_path,
                content=content,
                summary=analysis.get("summary", content[:100]),
                keywords=analysis.get("keywords", []),
                strata=context.get("strata", "somatic")
            )
            
            if memory_created:
                # Évolution temporelle de la création de mémoire
                self.temporal_dimension.evolve("workspace_memory_created", {
                    "file_path": file_path,
                    "content_length": len(content),
                    "keywords_count": len(analysis.get("keywords", [])),
                    "strata": context.get("strata", "somatic")
                })
                
                # Apprentissage temporel
                self.learn_from_interaction({
                    "type": "workspace_memory_creation",
                    "file_path": file_path,
                    "content_length": len(content),
                    "strata": context.get("strata", "somatic")
                })
            
            return memory_created
            
        except Exception as e:
            # Gestion d'erreur avec évolution temporelle
            self.temporal_dimension.evolve("workspace_memory_creation_error", {
                "file_path": file_path,
                "error": str(e)
            })
            return False
    
    async def _analyze_file(self, file_path: str, content: str) -> Dict[str, Any]:
        """Analyse de fichier avec apprentissage temporel"""
        analysis = {
            "file_path": file_path,
            "content_length": len(content),
            "summary": content[:100] + "..." if len(content) > 100 else content,
            "keywords": [],
            "code_patterns": []
        }
        
        # Extraction de mots-clés
        analysis["keywords"] = await self._extract_keywords(content)
        
        # Extraction de patterns de code
        analysis["code_patterns"] = await self._extract_code_patterns(content)
        
        # Apprentissage temporel de l'analyse
        self.learn_from_interaction({
            "type": "file_analysis",
            "file_path": file_path,
            "content_length": len(content),
            "keywords_count": len(analysis["keywords"]),
            "patterns_count": len(analysis["code_patterns"])
        })
        
        return analysis
    
    async def _extract_code_patterns(self, content: str) -> List[str]:
        """Extraction de patterns de code avec cache temporel"""
        # Vérification du cache
        cache_key = hash(content)
        if cache_key in self.code_patterns_cache:
            return self.code_patterns_cache[cache_key]
        
        patterns = []
        
        # Patterns simples
        if "class " in content:
            patterns.append("class_definition")
        if "def " in content:
            patterns.append("function_definition")
        if "import " in content:
            patterns.append("import_statement")
        if "async " in content:
            patterns.append("async_code")
        
        # Mise en cache
        self.code_patterns_cache[cache_key] = patterns
        
        return patterns
    
    async def _extract_keywords(self, content: str) -> List[str]:
        """Extraction de mots-clés avec apprentissage temporel"""
        # Extraction simple basée sur les mots fréquents
        words = re.findall(r'\b\w+\b', content.lower())
        word_freq = {}
        
        for word in words:
            if len(word) > 3:  # Ignorer les mots trop courts
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Sélection des mots les plus fréquents
        keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
        keyword_list = [word for word, freq in keywords]
        
        return keyword_list
    
    async def analyze_workspace_structure(self) -> Dict[str, Any]:
        """Analyse de la structure workspace avec tracking temporel"""
        try:
            structure = {
                "workspace_path": str(self.workspace_path),
                "files": [],
                "directories": [],
                "total_files": 0,
                "total_directories": 0,
                "file_types": {},
                "analysis_timestamp": datetime.now().isoformat()
            }
            
            # Analyse récursive
            for root, dirs, files in os.walk(self.workspace_path):
                # Directories
                for dir_name in dirs:
                    structure["directories"].append(os.path.join(root, dir_name))
                    structure["total_directories"] += 1
                
                # Files
                for file_name in files:
                    file_path = os.path.join(root, file_name)
                    structure["files"].append(file_path)
                    structure["total_files"] += 1
                    
                    # Types de fichiers
                    file_ext = Path(file_name).suffix
                    structure["file_types"][file_ext] = structure["file_types"].get(file_ext, 0) + 1
            
            # Évolution temporelle de l'analyse
            self.temporal_dimension.evolve("workspace_structure_analyzed", {
                "total_files": structure["total_files"],
                "total_directories": structure["total_directories"],
                "file_types_count": len(structure["file_types"])
            })
            
            return structure
            
        except Exception as e:
            # Gestion d'erreur avec évolution temporelle
            self.temporal_dimension.evolve("workspace_structure_analysis_error", {
                "error": str(e)
            })
            return {}
    
    async def track_development_flow(self, action: str, context: Dict[str, Any] = None) -> bool:
        """Tracking du flux de développement avec évolution temporelle"""
        try:
            context = context or {}
            
            # Tracking temporel de l'action
            self.temporal_dimension.evolve("development_action_tracked", {
                "action": action,
                "context": context,
                "timestamp": datetime.now().isoformat()
            })
            
            # Apprentissage temporel
            self.learn_from_interaction({
                "type": "development_action",
                "action": action,
                "context": context
            })
            
            return True
            
        except Exception as e:
            # Gestion d'erreur avec évolution temporelle
            self.temporal_dimension.evolve("development_flow_tracking_error", {
                "action": action,
                "error": str(e)
            })
            return False
    
    def get_entity_specific_data(self) -> Dict[str, Any]:
        """Données spécifiques à la couche workspace temporelle"""
        return {
            "workspace_path": str(self.workspace_path),
            "llm_provider_available": self.llm_provider is not None,
            "code_patterns_cache_size": len(self.code_patterns_cache),
            "search_engine_initialized": hasattr(self, 'search_engine')
        } 