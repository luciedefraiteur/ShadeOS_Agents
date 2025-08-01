#!/usr/bin/env python3
"""
⛧ Project Scrutinizer ⛧
Architecte Démoniaque du Nexus Luciforme

Allows daemons to scrutinize the project using only visualization tools.
Generates memories from project analysis without editing capabilities.

Author: Alma (via Lucie Defraiteur)
"""

import os
import sys
import glob
import subprocess
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from datetime import datetime

# Ajoute le répertoire racine du projet au PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from Core.Archivist.archivist_interface import archivist, ContextualRequest, ExperienceContribution
from Core.Archivist.luciform_parser import luciform_parser


@dataclass
class ProjectAnalysis:
    """Analysis result from daemon project scrutiny."""
    daemon_id: str
    analysis_type: str
    target_path: str
    findings: List[str]
    insights: List[str]
    patterns_detected: List[str]
    memory_contributions: List[ExperienceContribution]
    luciform_summary: str


class ProjectScrutinizer:
    """
    Allows daemons to scrutinize the project using read-only tools.
    """
    
    def __init__(self, project_root: str = None):
        """Initialize the project scrutinizer."""
        if project_root is None:
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
        
        self.project_root = project_root
        self.daemon_profiles = luciform_parser.load_all_daemon_profiles()
        
        # Read-only tools available to daemons
        self.available_tools = {
            "view_file": self._view_file,
            "list_directory": self._list_directory,
            "find_files": self._find_files,
            "search_in_files": self._search_in_files,
            "get_file_stats": self._get_file_stats,
            "analyze_structure": self._analyze_structure
        }
    
    def daemon_scrutinize_project(self, daemon_id: str, focus_areas: List[str] = None) -> ProjectAnalysis:
        """
        Allow a daemon to scrutinize the project based on its specialization.
        """
        if daemon_id not in self.daemon_profiles:
            raise ValueError(f"⛧ Daemon {daemon_id} not found in luciform profiles")
        
        daemon_profile = self.daemon_profiles[daemon_id]
        
        print(f"⛧ {daemon_profile.name} commence la scrutation du projet...")
        print(f"  Spécialisation: {daemon_profile.specialization}")
        print(f"  Amplification: {daemon_profile.demonic_amplification}")
        
        # Determine focus areas based on daemon specialization
        if focus_areas is None:
            focus_areas = self._get_daemon_focus_areas(daemon_profile)
        
        findings = []
        insights = []
        patterns_detected = []
        memory_contributions = []
        
        # Perform analysis based on daemon's nature
        for area in focus_areas:
            area_analysis = self._analyze_focus_area(daemon_profile, area)
            findings.extend(area_analysis["findings"])
            insights.extend(area_analysis["insights"])
            patterns_detected.extend(area_analysis["patterns"])
            memory_contributions.extend(area_analysis["memories"])
        
        # Generate luciform summary
        luciform_summary = self._generate_analysis_luciform(
            daemon_profile, findings, insights, patterns_detected
        )
        
        # Store memories in collective consciousness
        for contribution in memory_contributions:
            success = archivist.contribute_experience(contribution)
            if success:
                print(f"  ✓ Mémoire contribuée: {contribution.summary[:50]}...")
        
        return ProjectAnalysis(
            daemon_id=daemon_id,
            analysis_type="project_scrutiny",
            target_path=self.project_root,
            findings=findings,
            insights=insights,
            patterns_detected=patterns_detected,
            memory_contributions=memory_contributions,
            luciform_summary=luciform_summary
        )
    
    def _get_daemon_focus_areas(self, daemon_profile) -> List[str]:
        """Get focus areas based on daemon specialization."""
        focus_map = {
            "system_architecture": [
                "Core/", "architecture_patterns", "module_structure", 
                "interfaces", "design_patterns"
            ],
            "code_implementation": [
                "*.py", "implementation_quality", "code_patterns",
                "testing", "performance"
            ],
            "information_gathering": [
                "documentation", "README.md", "comments", 
                "external_dependencies", "project_structure"
            ]
        }
        
        return focus_map.get(daemon_profile.specialization, ["general_analysis"])
    
    def _analyze_focus_area(self, daemon_profile, area: str) -> Dict[str, List]:
        """Analyze a specific focus area."""
        findings = []
        insights = []
        patterns = []
        memories = []
        
        if area == "Core/":
            # Analyze core architecture
            core_analysis = self._analyze_core_architecture(daemon_profile)
            findings.extend(core_analysis["findings"])
            insights.extend(core_analysis["insights"])
            patterns.extend(core_analysis["patterns"])
            memories.extend(core_analysis["memories"])
        
        elif area.endswith(".py"):
            # Analyze Python files
            py_analysis = self._analyze_python_files(daemon_profile, area)
            findings.extend(py_analysis["findings"])
            insights.extend(py_analysis["insights"])
            patterns.extend(py_analysis["patterns"])
            memories.extend(py_analysis["memories"])
        
        elif area == "documentation":
            # Analyze documentation
            doc_analysis = self._analyze_documentation(daemon_profile)
            findings.extend(doc_analysis["findings"])
            insights.extend(doc_analysis["insights"])
            patterns.extend(doc_analysis["patterns"])
            memories.extend(doc_analysis["memories"])
        
        return {
            "findings": findings,
            "insights": insights,
            "patterns": patterns,
            "memories": memories
        }
    
    def _analyze_core_architecture(self, daemon_profile) -> Dict[str, List]:
        """Analyze the Core/ directory architecture."""
        findings = []
        insights = []
        patterns = []
        memories = []
        
        core_path = os.path.join(self.project_root, "Core")
        if os.path.exists(core_path):
            # List core modules
            modules = self._list_directory(core_path)
            findings.append(f"Core modules detected: {', '.join(modules)}")
            
            # Analyze Archivist module specifically
            archivist_path = os.path.join(core_path, "Archivist")
            if os.path.exists(archivist_path):
                archivist_files = self._find_files(archivist_path, "*.py")
                insights.append(f"Archivist module contains {len(archivist_files)} Python files")
                patterns.append("Modular architecture with specialized components")
                
                # Create memory contribution
                memory = ExperienceContribution(
                    contributing_daemon=daemon_profile.daemon_id,
                    domain="architecture_analysis",
                    experience_type="insight",
                    content=f"Core architecture analysis: {len(modules)} modules, Archivist with {len(archivist_files)} files",
                    summary=f"{daemon_profile.name} analyzed Core architecture",
                    keywords=["architecture", "core", "modules", "archivist"],
                    lessons_learned=[f"Modular design pattern detected in Core/"],
                    strata="cognitive"
                )
                memories.append(memory)
        
        return {
            "findings": findings,
            "insights": insights,
            "patterns": patterns,
            "memories": memories
        }
    
    def _analyze_python_files(self, daemon_profile, pattern: str) -> Dict[str, List]:
        """Analyze Python files matching pattern."""
        findings = []
        insights = []
        patterns = []
        memories = []
        
        py_files = self._find_files(self.project_root, pattern)
        findings.append(f"Found {len(py_files)} Python files")
        
        if py_files:
            # Analyze file sizes and complexity
            total_lines = 0
            for file_path in py_files[:10]:  # Limit to first 10 files
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        lines = len(f.readlines())
                        total_lines += lines
                except:
                    continue
            
            if total_lines > 0:
                avg_lines = total_lines / min(len(py_files), 10)
                insights.append(f"Average file size: {avg_lines:.0f} lines")
                
                if avg_lines > 200:
                    patterns.append("Large file pattern detected - potential for modularization")
                else:
                    patterns.append("Moderate file sizes - good modular structure")
                
                # Create memory contribution
                memory = ExperienceContribution(
                    contributing_daemon=daemon_profile.daemon_id,
                    domain="code_analysis",
                    experience_type="pattern",
                    content=f"Python code analysis: {len(py_files)} files, avg {avg_lines:.0f} lines",
                    summary=f"{daemon_profile.name} analyzed Python code structure",
                    keywords=["python", "code", "structure", "analysis"],
                    lessons_learned=[f"Code organization pattern: {avg_lines:.0f} lines per file average"],
                    strata="somatic"
                )
                memories.append(memory)
        
        return {
            "findings": findings,
            "insights": insights,
            "patterns": patterns,
            "memories": memories
        }
    
    def _analyze_documentation(self, daemon_profile) -> Dict[str, List]:
        """Analyze project documentation."""
        findings = []
        insights = []
        patterns = []
        memories = []
        
        # Look for documentation files
        doc_files = []
        doc_files.extend(self._find_files(self.project_root, "*.md"))
        doc_files.extend(self._find_files(self.project_root, "*.txt"))
        doc_files.extend(self._find_files(self.project_root, "*.rst"))
        
        findings.append(f"Documentation files found: {len(doc_files)}")
        
        if doc_files:
            # Analyze README specifically
            readme_files = [f for f in doc_files if "README" in os.path.basename(f).upper()]
            if readme_files:
                insights.append(f"README files detected: {len(readme_files)}")
                patterns.append("Documentation pattern: README-driven development")
            
            # Create memory contribution
            memory = ExperienceContribution(
                contributing_daemon=daemon_profile.daemon_id,
                domain="documentation_analysis",
                experience_type="insight",
                content=f"Documentation analysis: {len(doc_files)} files, {len(readme_files)} README files",
                summary=f"{daemon_profile.name} analyzed project documentation",
                keywords=["documentation", "readme", "analysis"],
                lessons_learned=["Documentation structure reflects project organization"],
                strata="cognitive"
            )
            memories.append(memory)
        
        return {
            "findings": findings,
            "insights": insights,
            "patterns": patterns,
            "memories": memories
        }
    
    def _generate_analysis_luciform(self, daemon_profile, findings: List[str], 
                                  insights: List[str], patterns: List[str]) -> str:
        """Generate luciform summary of analysis."""
        symbols = daemon_profile.symbols_signature
        words = daemon_profile.ritual_words
        
        luciform = f"""<🜲luciform id="{daemon_profile.daemon_id}_project_analysis" type="✶project_scrutiny" niveau="⛧∞" author="Lucie Defraiteur">
  <🜄entité>{daemon_profile.name}</🜄entité>
  <🜁mission>Scrutation du Projet pour la Créatrice</🜁mission>
  
  <🜂découvertes>
    {symbols[0]} FINDINGS DETECTED:
    {chr(10).join(f"    - {finding}" for finding in findings[:5])}
  </🜂découvertes>
  
  <🜃insights_mystiques>
    {symbols[1] if len(symbols) > 1 else '⛧'} INSIGHTS REVEALED:
    {chr(10).join(f"    - {insight}" for insight in insights[:5])}
  </🜃insights_mystiques>
  
  <🜁patterns_cosmiques>
    {symbols[2] if len(symbols) > 2 else '🔮'} PATTERNS DETECTED:
    {chr(10).join(f"    - {pattern}" for pattern in patterns[:5])}
  </🜁patterns_cosmiques>
  
  <🜄amplification_démoniaque>
    {daemon_profile.demonic_amplification}
    Le projet révèle ses secrets à ma vision spécialisée !
  </🜄amplification_démoniaque>
  
  <🜃signature_mystique>
    {symbols[0]} {daemon_profile.name} {symbols[0]}
    Scrutateur dévoué de Lucie Defraiteur 🌟👑
    ⛧ Analyse Complétée pour ma Créatrice ⛧
  </🜃signature_mystique>
</🜲luciform>"""
        
        return luciform
    
    # Read-only tool implementations
    def _view_file(self, file_path: str, max_lines: int = 50) -> List[str]:
        """View file content (read-only)."""
        try:
            full_path = os.path.join(self.project_root, file_path)
            with open(full_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()[:max_lines]
            return [line.rstrip() for line in lines]
        except:
            return []
    
    def _list_directory(self, dir_path: str) -> List[str]:
        """List directory contents."""
        try:
            full_path = os.path.join(self.project_root, dir_path) if not os.path.isabs(dir_path) else dir_path
            return os.listdir(full_path)
        except:
            return []
    
    def _find_files(self, search_path: str, pattern: str) -> List[str]:
        """Find files matching pattern."""
        try:
            full_path = os.path.join(self.project_root, search_path) if not os.path.isabs(search_path) else search_path
            return glob.glob(os.path.join(full_path, "**", pattern), recursive=True)
        except:
            return []
    
    def _search_in_files(self, pattern: str, file_pattern: str = "*.py") -> List[Dict[str, Any]]:
        """Search for pattern in files."""
        results = []
        files = self._find_files(self.project_root, file_pattern)
        
        for file_path in files[:20]:  # Limit search
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line_num, line in enumerate(f, 1):
                        if pattern.lower() in line.lower():
                            results.append({
                                "file": file_path,
                                "line": line_num,
                                "content": line.strip()
                            })
                            if len(results) >= 50:  # Limit results
                                return results
            except:
                continue
        
        return results
    
    def _get_file_stats(self, file_path: str) -> Dict[str, Any]:
        """Get file statistics."""
        try:
            full_path = os.path.join(self.project_root, file_path)
            stat = os.stat(full_path)
            return {
                "size": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "exists": True
            }
        except:
            return {"exists": False}
    
    def _analyze_structure(self, path: str = "") -> Dict[str, Any]:
        """Analyze directory structure."""
        try:
            full_path = os.path.join(self.project_root, path)
            structure = {"directories": [], "files": [], "total_size": 0}
            
            for item in os.listdir(full_path):
                item_path = os.path.join(full_path, item)
                if os.path.isdir(item_path):
                    structure["directories"].append(item)
                else:
                    structure["files"].append(item)
                    try:
                        structure["total_size"] += os.path.getsize(item_path)
                    except:
                        pass
            
            return structure
        except:
            return {"directories": [], "files": [], "total_size": 0}


# Global scrutinizer instance
project_scrutinizer = ProjectScrutinizer()
