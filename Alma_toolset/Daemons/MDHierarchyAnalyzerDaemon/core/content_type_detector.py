#!/usr/bin/env python3
"""
🔍 Content Type Detector

Détecteur intelligent du type de contenu pour cascade adaptative.
Distingue CODE, DOCUMENTATION, MIXED, CONFIGURATION selon analyse fine.

Créé par Alma, Architecte Démoniaque du Nexus Luciforme.
"""

import re
from enum import Enum
from pathlib import Path
from typing import Tuple, Dict, List
from dataclasses import dataclass


class ContentType(Enum):
    """Types de contenu détectés."""
    
    CODE = "code"
    DOCUMENTATION = "documentation"
    MIXED = "mixed"
    CONFIGURATION = "configuration"
    UNKNOWN = "unknown"


@dataclass
class ContentCharacteristics:
    """Caractéristiques détaillées du contenu."""
    
    content_type: ContentType
    code_ratio: float              # 0.0-1.0
    documentation_ratio: float     # 0.0-1.0
    structural_complexity: float   # Complexité structurelle
    narrative_flow: float          # Flux narratif
    technical_density: float       # Densité technique
    language_detected: str         # Langage détecté
    confidence_score: float        # Confiance de la détection


class ContentTypeDetector:
    """Détecteur intelligent du type de contenu."""
    
    def __init__(self):
        # Extensions par type
        self.code_extensions = {
            '.py', '.js', '.ts', '.jsx', '.tsx', '.rs', '.go', '.java', 
            '.cpp', '.c', '.h', '.hpp', '.cs', '.php', '.rb', '.swift',
            '.kt', '.scala', '.clj', '.hs', '.ml', '.fs', '.dart'
        }
        
        self.doc_extensions = {
            '.md', '.rst', '.txt', '.adoc', '.org', '.tex', '.wiki'
        }
        
        self.config_extensions = {
            '.json', '.yaml', '.yml', '.toml', '.ini', '.cfg', '.conf',
            '.xml', '.properties', '.env'
        }
        
        # Patterns de code
        self.code_patterns = [
            r'\bdef\s+\w+\s*\(',           # Python functions
            r'\bclass\s+\w+',              # Class definitions
            r'\bfunction\s+\w+\s*\(',      # JS functions
            r'\bimport\s+\w+',             # Imports
            r'\bfrom\s+\w+\s+import',      # Python imports
            r'\bconst\s+\w+\s*=',          # JS const
            r'\blet\s+\w+\s*=',            # JS let
            r'\bvar\s+\w+\s*=',            # JS var
            r'\bfn\s+\w+\s*\(',            # Rust functions
            r'\bfunc\s+\w+\s*\(',          # Go functions
            r'\bpublic\s+\w+',             # Java/C# public
            r'\bprivate\s+\w+',            # Java/C# private
            r'\breturn\s+',                # Return statements
            r'\bif\s*\(',                  # If statements
            r'\bfor\s*\(',                 # For loops
            r'\bwhile\s*\(',               # While loops
        ]
        
        # Patterns de documentation
        self.doc_patterns = [
            r'^#+\s+',                     # Markdown headers
            r'^\*\s+',                     # Bullet points
            r'^\d+\.\s+',                  # Numbered lists
            r'\[.*\]\(.*\)',               # Markdown links
            r'\*\*.*\*\*',                 # Bold text
            r'\*.*\*',                     # Italic text
            r'`.*`',                       # Inline code
            r'^>\s+',                      # Blockquotes
            r'^\|.*\|',                    # Tables
        ]
    
    def detect_content_type(self, file_path: str, content: str) -> ContentCharacteristics:
        """Détecte le type de contenu avec analyse complète."""
        
        # Détection par extension
        extension_type = self._detect_by_extension(file_path)
        
        # Analyse du contenu
        code_ratio, doc_ratio = self._analyze_content_ratio(content)
        structural_complexity = self._calculate_structural_complexity(content)
        narrative_flow = self._calculate_narrative_flow(content)
        technical_density = self._calculate_technical_density(content)
        language_detected = self._detect_language(file_path, content)
        
        # Détermination du type final
        final_type, confidence = self._determine_final_type(
            extension_type, code_ratio, doc_ratio, content
        )
        
        return ContentCharacteristics(
            content_type=final_type,
            code_ratio=code_ratio,
            documentation_ratio=doc_ratio,
            structural_complexity=structural_complexity,
            narrative_flow=narrative_flow,
            technical_density=technical_density,
            language_detected=language_detected,
            confidence_score=confidence
        )
    
    def _detect_by_extension(self, file_path: str) -> ContentType:
        """Détection basique par extension."""
        
        ext = Path(file_path).suffix.lower()
        
        if ext in self.code_extensions:
            return ContentType.CODE
        elif ext in self.doc_extensions:
            return ContentType.DOCUMENTATION
        elif ext in self.config_extensions:
            return ContentType.CONFIGURATION
        else:
            return ContentType.UNKNOWN
    
    def _analyze_content_ratio(self, content: str) -> Tuple[float, float]:
        """Analyse le ratio code vs documentation."""
        
        lines = content.split('\n')
        code_score = 0
        doc_score = 0
        total_lines = 0
        
        for line in lines:
            stripped = line.strip()
            if not stripped or stripped.startswith('#'):  # Skip empty and comments
                continue
                
            total_lines += 1
            line_code_score = 0
            line_doc_score = 0
            
            # Score de code pour cette ligne
            for pattern in self.code_patterns:
                if re.search(pattern, stripped):
                    line_code_score += 2
            
            # Indicateurs de code supplémentaires
            if any(char in stripped for char in '{}();=[]'):
                line_code_score += 1
            if any(keyword in stripped.lower() for keyword in ['def', 'class', 'function', 'import']):
                line_code_score += 2
            
            # Score de documentation pour cette ligne
            for pattern in self.doc_patterns:
                if re.search(pattern, stripped, re.MULTILINE):
                    line_doc_score += 2
            
            # Indicateurs de documentation supplémentaires
            if len(stripped.split()) > 8 and not any(char in stripped for char in '{}();'):
                line_doc_score += 1
            if any(word in stripped.lower() for word in ['the', 'this', 'that', 'with', 'from']):
                line_doc_score += 0.5
            
            code_score += line_code_score
            doc_score += line_doc_score
        
        if total_lines == 0:
            return 0.5, 0.5
        
        total_score = code_score + doc_score
        if total_score == 0:
            return 0.5, 0.5
        
        return code_score / total_score, doc_score / total_score
    
    def _calculate_structural_complexity(self, content: str) -> float:
        """Calcule la complexité structurelle."""
        
        lines = content.split('\n')
        complexity_score = 0
        
        # Indicateurs de complexité
        nesting_level = 0
        max_nesting = 0
        
        for line in lines:
            stripped = line.strip()
            
            # Nesting (indentation ou accolades)
            if stripped.endswith(':') or stripped.endswith('{'):
                nesting_level += 1
                max_nesting = max(max_nesting, nesting_level)
            elif stripped.startswith('}') or (len(line) - len(line.lstrip()) < nesting_level * 4):
                nesting_level = max(0, nesting_level - 1)
            
            # Structures de contrôle
            if any(keyword in stripped for keyword in ['if', 'for', 'while', 'try', 'catch']):
                complexity_score += 1
            
            # Définitions de fonctions/classes
            if any(keyword in stripped for keyword in ['def', 'class', 'function']):
                complexity_score += 2
        
        # Normalisation
        total_lines = len([l for l in lines if l.strip()])
        if total_lines == 0:
            return 0.0
        
        structural_score = (complexity_score + max_nesting * 2) / total_lines
        return min(1.0, structural_score)
    
    def _calculate_narrative_flow(self, content: str) -> float:
        """Calcule le flux narratif."""
        
        lines = content.split('\n')
        flow_score = 0
        
        # Indicateurs de flux narratif
        for line in lines:
            stripped = line.strip()
            
            # Headers et structure
            if re.match(r'^#+\s+', stripped):
                flow_score += 2
            
            # Listes et énumérations
            if re.match(r'^[\*\-\+]\s+', stripped) or re.match(r'^\d+\.\s+', stripped):
                flow_score += 1
            
            # Phrases longues (narratif)
            if len(stripped.split()) > 10:
                flow_score += 1
            
            # Connecteurs logiques
            if any(connector in stripped.lower() for connector in 
                   ['however', 'therefore', 'moreover', 'furthermore', 'consequently']):
                flow_score += 1
        
        # Normalisation
        total_lines = len([l for l in lines if l.strip()])
        if total_lines == 0:
            return 0.0
        
        return min(1.0, flow_score / total_lines)
    
    def _calculate_technical_density(self, content: str) -> float:
        """Calcule la densité technique."""
        
        # Mots techniques communs
        technical_terms = [
            'algorithm', 'function', 'class', 'method', 'variable', 'parameter',
            'return', 'import', 'module', 'library', 'framework', 'api',
            'database', 'query', 'server', 'client', 'protocol', 'interface',
            'implementation', 'architecture', 'design', 'pattern', 'structure'
        ]
        
        words = content.lower().split()
        technical_count = sum(1 for word in words if any(term in word for term in technical_terms))
        
        if len(words) == 0:
            return 0.0
        
        return min(1.0, technical_count / len(words) * 10)  # Amplification pour visibilité
    
    def _detect_language(self, file_path: str, content: str) -> str:
        """Détecte le langage de programmation ou type de document."""
        
        ext = Path(file_path).suffix.lower()
        
        # Mapping extensions → langages
        language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.jsx': 'react',
            '.tsx': 'react-typescript',
            '.rs': 'rust',
            '.go': 'go',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.cs': 'csharp',
            '.php': 'php',
            '.rb': 'ruby',
            '.md': 'markdown',
            '.rst': 'restructuredtext',
            '.json': 'json',
            '.yaml': 'yaml',
            '.yml': 'yaml',
            '.toml': 'toml'
        }
        
        if ext in language_map:
            return language_map[ext]
        
        # Détection par contenu
        if 'def ' in content and 'import ' in content:
            return 'python'
        elif 'function' in content and ('{' in content or '=>' in content):
            return 'javascript'
        elif 'fn ' in content and 'let ' in content:
            return 'rust'
        elif 'func ' in content and 'package ' in content:
            return 'go'
        
        return 'unknown'
    
    def _determine_final_type(self, extension_type: ContentType, 
                            code_ratio: float, doc_ratio: float, 
                            content: str) -> Tuple[ContentType, float]:
        """Détermine le type final avec score de confiance."""
        
        confidence = 0.5
        
        # Si extension claire et ratios cohérents
        if extension_type == ContentType.CODE and code_ratio > 0.6:
            return ContentType.CODE, 0.9
        elif extension_type == ContentType.DOCUMENTATION and doc_ratio > 0.6:
            return ContentType.DOCUMENTATION, 0.9
        elif extension_type == ContentType.CONFIGURATION:
            return ContentType.CONFIGURATION, 0.8
        
        # Analyse par ratios
        if code_ratio > 0.7:
            return ContentType.CODE, 0.8
        elif doc_ratio > 0.7:
            return ContentType.DOCUMENTATION, 0.8
        elif abs(code_ratio - doc_ratio) < 0.2:
            return ContentType.MIXED, 0.7
        
        # Fallback sur extension
        if extension_type != ContentType.UNKNOWN:
            return extension_type, 0.6
        
        # Dernier recours
        if code_ratio > doc_ratio:
            return ContentType.CODE, 0.5
        else:
            return ContentType.DOCUMENTATION, 0.5


def test_content_type_detector():
    """Test du détecteur de type de contenu."""
    
    print("🔍 Testing Content Type Detector...")
    
    detector = ContentTypeDetector()
    
    # Test cases
    test_cases = [
        # Code Python
        ("test.py", """
def hello_world():
    print("Hello, World!")
    return True

class MyClass:
    def __init__(self):
        self.value = 42
""", ContentType.CODE),
        
        # Documentation Markdown
        ("README.md", """
# Project Title

This is a comprehensive guide to using our amazing project.

## Features

- Easy to use
- Well documented
- Highly performant

## Installation

Follow these steps to install the project:

1. Clone the repository
2. Install dependencies
3. Run the application
""", ContentType.DOCUMENTATION),
        
        # Contenu mixte
        ("tutorial.md", """
# Python Tutorial

Here's how to create a function:

```python
def my_function():
    return "Hello"
```

This function demonstrates basic Python syntax.
""", ContentType.MIXED),
        
        # Configuration
        ("config.json", """
{
    "name": "my-app",
    "version": "1.0.0",
    "dependencies": {
        "express": "^4.18.0"
    }
}
""", ContentType.CONFIGURATION)
    ]
    
    for file_path, content, expected_type in test_cases:
        characteristics = detector.detect_content_type(file_path, content)
        
        print(f"\n📄 File: {file_path}")
        print(f"  🎯 Detected: {characteristics.content_type.value}")
        print(f"  📊 Expected: {expected_type.value}")
        print(f"  ✅ Match: {'Yes' if characteristics.content_type == expected_type else 'No'}")
        print(f"  📈 Confidence: {characteristics.confidence_score:.2f}")
        print(f"  💻 Code ratio: {characteristics.code_ratio:.2f}")
        print(f"  📚 Doc ratio: {characteristics.documentation_ratio:.2f}")
        print(f"  🔧 Complexity: {characteristics.structural_complexity:.2f}")
        print(f"  📖 Narrative: {characteristics.narrative_flow:.2f}")
        print(f"  🎓 Technical: {characteristics.technical_density:.2f}")
        print(f"  🗣️ Language: {characteristics.language_detected}")


if __name__ == "__main__":
    test_content_type_detector()
