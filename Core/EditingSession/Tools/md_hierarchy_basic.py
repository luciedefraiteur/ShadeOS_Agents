#!/usr/bin/env python3
"""
🗂️ Organisateur Basique de Fichiers Markdown - Version 1.0

Outil simple pour lister les fichiers .md par ordre de récence.
Version basique focalisée sur la fonctionnalité essentielle.

Créé par Alma, Architecte Démoniaque du Nexus Luciforme.
"""

import os
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Tuple
from dataclasses import dataclass


@dataclass
class BasicMDFile:
    """Information basique sur un fichier Markdown."""
    
    path: str
    name: str
    size: int
    modified_time: datetime
    relative_path: str
    days_old: int
    is_recent: bool


class BasicMDOrganizer:
    """Organisateur basique de fichiers Markdown."""

    def __init__(self, root_path: str = ".", recent_threshold_days: int = 7,
                 exclude_dirs: List[str] = None):
        self.root_path = Path(root_path).resolve()
        self.recent_threshold = timedelta(days=recent_threshold_days)
        self.exclude_dirs = exclude_dirs or ["ShadeOS", ".git", "__pycache__", "node_modules"]
        self.files: List[BasicMDFile] = []
    
    def scan_markdown_files(self) -> List[BasicMDFile]:
        """Scanne tous les fichiers Markdown en excluant certains répertoires."""

        print(f"🔍 Scanning Markdown files in: {self.root_path}")
        if self.exclude_dirs:
            print(f"🚫 Excluding directories: {', '.join(self.exclude_dirs)}")

        self.files = []

        for md_file in self.root_path.rglob("*.md"):
            if md_file.is_file() and not self._is_excluded(md_file):
                try:
                    file_info = self._analyze_basic_file(md_file)
                    self.files.append(file_info)
                except Exception as e:
                    print(f"⚠️ Error analyzing {md_file}: {e}")

        # Tri par date de modification (plus récent en premier)
        self.files.sort(key=lambda f: f.modified_time, reverse=True)

        print(f"✅ Found {len(self.files)} Markdown files")
        return self.files
    
    def _analyze_basic_file(self, file_path: Path) -> BasicMDFile:
        """Analyse basique d'un fichier."""
        
        stat = file_path.stat()
        modified_time = datetime.fromtimestamp(stat.st_mtime)
        relative_path = str(file_path.relative_to(self.root_path))
        
        # Calcul de l'âge
        now = datetime.now()
        days_old = (now - modified_time).days
        is_recent = (now - modified_time) <= self.recent_threshold
        
        return BasicMDFile(
            path=str(file_path),
            name=file_path.name,
            size=stat.st_size,
            modified_time=modified_time,
            relative_path=relative_path,
            days_old=days_old,
            is_recent=is_recent
        )

    def _is_excluded(self, file_path: Path) -> bool:
        """Vérifie si un fichier doit être exclu."""

        # Vérifie si le fichier est dans un répertoire exclu
        for exclude_dir in self.exclude_dirs:
            if exclude_dir in file_path.parts:
                return True

        return False
    
    def generate_report(self, output_file: str = "MD_RECENT_FILES.md") -> str:
        """Génère un rapport simple par récence."""
        
        if not self.files:
            self.scan_markdown_files()
        
        # Séparation par récence
        recent_files = [f for f in self.files if f.is_recent]
        older_files = [f for f in self.files if not f.is_recent]
        
        # Génération du rapport
        report_lines = [
            "# 📅 Fichiers Markdown par Récence",
            "",
            f"**Généré le :** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  ",
            f"**Répertoire :** `{self.root_path}`  ",
            f"**Total fichiers :** {len(self.files)}  ",
            f"**Fichiers récents :** {len(recent_files)} (< {self.recent_threshold.days} jours)  ",
            f"**Fichiers plus anciens :** {len(older_files)}  ",
            "",
            "---",
            ""
        ]
        
        # Section fichiers récents
        if recent_files:
            report_lines.extend([
                f"## 🔥 Fichiers Récents ({len(recent_files)} fichiers)",
                "",
                "*Modifiés dans les derniers jours*",
                ""
            ])
            
            for file_info in recent_files:
                modified_str = file_info.modified_time.strftime('%Y-%m-%d %H:%M')
                size_kb = file_info.size // 1024 if file_info.size > 1024 else file_info.size
                size_unit = "KB" if file_info.size > 1024 else "B"
                
                report_lines.append(
                    f"- **{file_info.name}** "
                    f"*({file_info.days_old} jour{'s' if file_info.days_old > 1 else ''} - "
                    f"{modified_str} - {size_kb} {size_unit})*  "
                    f"  📁 `{file_info.relative_path}`"
                )
            
            report_lines.append("")
        
        # Section fichiers plus anciens
        if older_files:
            report_lines.extend([
                f"## 📚 Fichiers Plus Anciens ({len(older_files)} fichiers)",
                "",
                "*Modifiés il y a plus de 7 jours*",
                ""
            ])
            
            # Groupement par semaines pour les anciens
            weeks_groups = self._group_by_weeks(older_files)
            
            for week_label, week_files in weeks_groups.items():
                if week_files:
                    report_lines.extend([
                        f"### {week_label} ({len(week_files)} fichiers)",
                        ""
                    ])
                    
                    for file_info in week_files[:10]:  # Max 10 par groupe
                        modified_str = file_info.modified_time.strftime('%Y-%m-%d')
                        report_lines.append(
                            f"- **{file_info.name}** "
                            f"*({file_info.days_old} jours - {modified_str})*  "
                            f"  📁 `{file_info.relative_path}`"
                        )
                    
                    if len(week_files) > 10:
                        report_lines.append(f"  *... et {len(week_files) - 10} autres fichiers*")
                    
                    report_lines.append("")
        
        # Statistiques finales
        report_lines.extend([
            "---",
            "",
            "## 📊 Statistiques",
            "",
            f"- **Total :** {len(self.files)} fichiers Markdown",
            f"- **Récents :** {len(recent_files)} fichiers (< {self.recent_threshold.days} jours)",
            f"- **Anciens :** {len(older_files)} fichiers",
            f"- **Taille totale :** {sum(f.size for f in self.files) // 1024} KB",
            "",
            f"*Rapport généré par md_hierarchy_basic.py le {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*"
        ])
        
        # Écriture du rapport
        report_content = '\n'.join(report_lines)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"✅ Rapport généré : {output_file}")
        return output_file
    
    def _group_by_weeks(self, files: List[BasicMDFile]) -> dict:
        """Groupe les fichiers par semaines."""
        
        groups = {
            "Semaine dernière (8-14 jours)": [],
            "Il y a 2-3 semaines (15-21 jours)": [],
            "Il y a 1 mois (22-30 jours)": [],
            "Il y a 2-3 mois (31-90 jours)": [],
            "Plus de 3 mois (90+ jours)": []
        }
        
        for file_info in files:
            days = file_info.days_old
            
            if 8 <= days <= 14:
                groups["Semaine dernière (8-14 jours)"].append(file_info)
            elif 15 <= days <= 21:
                groups["Il y a 2-3 semaines (15-21 jours)"].append(file_info)
            elif 22 <= days <= 30:
                groups["Il y a 1 mois (22-30 jours)"].append(file_info)
            elif 31 <= days <= 90:
                groups["Il y a 2-3 mois (31-90 jours)"].append(file_info)
            else:
                groups["Plus de 3 mois (90+ jours)"].append(file_info)
        
        # Tri dans chaque groupe par récence
        for group_files in groups.values():
            group_files.sort(key=lambda f: f.modified_time, reverse=True)
        
        return groups
    
    def print_summary(self):
        """Affiche un résumé dans la console."""
        
        if not self.files:
            self.scan_markdown_files()
        
        recent_count = len([f for f in self.files if f.is_recent])
        
        print("\n📊 Résumé :")
        print(f"  📁 Répertoire : {self.root_path}")
        print(f"  📄 Total fichiers : {len(self.files)}")
        print(f"  🔥 Récents : {recent_count}")
        print(f"  📚 Anciens : {len(self.files) - recent_count}")
        
        if self.files:
            print(f"  📅 Plus récent : {self.files[0].name} ({self.files[0].days_old} jours)")
            print(f"  📅 Plus ancien : {self.files[-1].name} ({self.files[-1].days_old} jours)")


def main():
    """Fonction principale."""
    
    parser = argparse.ArgumentParser(
        description="🗂️ Organisateur basique de fichiers Markdown par récence"
    )
    parser.add_argument(
        "--root", "-r", 
        default=".", 
        help="Répertoire racine à analyser (défaut: répertoire actuel)"
    )
    parser.add_argument(
        "--output", "-o", 
        default="MD_RECENT_FILES.md", 
        help="Fichier de rapport de sortie (défaut: MD_RECENT_FILES.md)"
    )
    parser.add_argument(
        "--recent-days", "-d", 
        type=int, 
        default=7, 
        help="Seuil de récence en jours (défaut: 7)"
    )
    parser.add_argument(
        "--summary-only", "-s",
        action="store_true",
        help="Affiche seulement le résumé sans générer de rapport"
    )
    parser.add_argument(
        "--exclude", "-e",
        nargs="*",
        default=["ShadeOS", ".git", "__pycache__", "node_modules"],
        help="Répertoires à exclure (défaut: ShadeOS .git __pycache__ node_modules)"
    )
    
    args = parser.parse_args()
    
    print("🗂️ MD Hierarchy Basic - Alma's Tool v1.0")
    print("=" * 50)
    
    # Création de l'organisateur
    organizer = BasicMDOrganizer(args.root, args.recent_days, args.exclude)
    
    # Scan des fichiers
    organizer.scan_markdown_files()
    
    # Affichage du résumé
    organizer.print_summary()
    
    # Génération du rapport (sauf si summary-only)
    if not args.summary_only:
        organizer.generate_report(args.output)
        print(f"\n🎉 Rapport généré avec succès : {args.output}")
    else:
        print("\n✅ Résumé affiché (pas de rapport généré)")


if __name__ == "__main__":
    main()
