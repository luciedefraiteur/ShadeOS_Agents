# 🔍 Outil Spécialisé V10ReadChunksUntilScopeTool

**Date :** 2025-08-07  
**Auteur :** Alma (via Lucie Defraiteur)  
**Contexte :** Outil spécialisé pour la fractalisation textuelle avec détection de scope  
**Statut :** Implémenté dans Core/Agents/V10/specialized_tools.py

---

## 🎯 **Objectif de l'Outil**

### **✅ Fonctionnalité Principale :**
L'outil `V10ReadChunksUntilScopeTool` est spécialement conçu pour la **fractalisation textuelle** avec détection intelligente de scopes. Il lit des chunks de code jusqu'à ce qu'un scope complet soit détecté, puis utilise l'LLM pour analyser le contenu.

### **✅ Cas d'Usage :**
- **Fichiers corrompus** : Quand l'AST ne peut pas être parsé
- **Syntaxe non-standard** : Code avec des patterns particuliers
- **Fallback textuel** : Alternative à l'analyse AST
- **Analyse LLM** : Compréhension sémantique du code

---

## 🔧 **Architecture de l'Outil :**

### **✅ V10ReadChunksUntilScopeTool :**
```python
class V10ReadChunksUntilScopeTool:
    """Outil spécialisé pour lire des chunks jusqu'au prochain scope complet."""
    
    def __init__(self, temporal_engine: TemporalFractalMemoryEngine):
        self.temporal_engine = temporal_engine
        self.scope_detector = V10ScopeDetector()
        self.llm_provider = V10LLMProvider()
```

### **✅ Workflow Complet :**

#### **1. Détection de Scope :**
```python
async def _detect_scope_boundaries(self, lines: List[str], start_line: int, 
                                 scope_type: str, max_chunks: int) -> Dict[str, Any]:
    """Détecte les limites du scope."""
    
    # Analyse des indentations et brackets
    indent_level = self._calculate_indent_level(line)
    bracket_count += line.count('[') - line.count(']')
    brace_count += line.count('{') - line.count('}')
    paren_count += line.count('(') - line.count(')')
    
    # Détection de fin de scope
    if self._is_scope_end(line, scope_patterns, indent_level, 
                         bracket_count, brace_count, paren_count):
        scope_end = line_num
        break
```

#### **2. Extraction de Contenu :**
```python
def _extract_scope_content(self, lines: List[str], scope_result: Dict) -> str:
    """Extrait le contenu du scope."""
    
    start = scope_result['start_line'] - 1
    end = scope_result['end_line']
    
    scope_lines = lines[start:end]
    return ''.join(scope_lines)
```

#### **3. Analyse LLM :**
```python
async def _analyze_scope_with_llm(self, scope_content: str, scope_type: str) -> Dict[str, Any]:
    """Analyse le scope avec LLM."""
    
    prompt = f"""
    Analyse ce bloc de code et fournis :
    1. Type de scope détecté
    2. Fonctionnalité principale
    3. Variables et fonctions définies
    4. Complexité estimée
    5. Suggestions d'amélioration
    
    Scope type: {scope_type}
    Contenu:
    {scope_content}
    """
```

#### **4. Création Fractale :**
```python
async def _create_fractal_scope_result(self, file_path: str, scope_content: str,
                                     scope_result: Dict, analysis: Dict) -> Dict[str, Any]:
    """Crée un résultat fractal pour le scope."""
    
    # Création d'un nœud temporal pour le scope
    scope_node = await self.temporal_engine.create_temporal_node(
        node_type="scope",
        content=scope_content,
        metadata={
            'file_path': file_path,
            'start_line': scope_result['start_line'],
            'end_line': scope_result['end_line'],
            'scope_type': scope_result['scope_type'],
            'analysis': analysis,
            'indent_level': scope_result['indent_level'],
            'lines_count': scope_result['end_line'] - scope_result['start_line'] + 1
        }
    )
```

---

## 🧠 **Détecteur de Scope Intelligent :**

### **✅ V10ScopeDetector :**
```python
class V10ScopeDetector:
    """Détecteur de scopes pour différents langages."""
    
    def __init__(self):
        self.scope_patterns = {
            'auto': {
                'start_patterns': [
                    r'^\s*(def|class|if|for|while|try|with|async def)\s+',
                    r'^\s*\{',
                    r'^\s*\[',
                    r'^\s*\('
                ],
                'end_patterns': [
                    r'^\s*$',  # Ligne vide
                    r'^\s*#',   # Commentaire
                    r'^\s*return\s+',
                    r'^\s*break\s*$',
                    r'^\s*continue\s*$'
                ]
            },
            'function': {
                'start_patterns': [
                    r'^\s*def\s+\w+\s*\(',
                    r'^\s*async\s+def\s+\w+\s*\(',
                    r'^\s*function\s+\w+\s*\(',
                    r'^\s*public\s+\w+\s+\w+\s*\(',
                    r'^\s*private\s+\w+\s+\w+\s*\('
                ],
                'end_patterns': [
                    r'^\s*return\s+',
                    r'^\s*pass\s*$',
                    r'^\s*raise\s+'
                ]
            },
            'class': {
                'start_patterns': [
                    r'^\s*class\s+\w+',
                    r'^\s*public\s+class\s+\w+',
                    r'^\s*private\s+class\s+\w+'
                ],
                'end_patterns': [
                    r'^\s*pass\s*$',
                    r'^\s*#\s*End\s+of\s+class'
                ]
            },
            'block': {
                'start_patterns': [
                    r'^\s*if\s+',
                    r'^\s*for\s+',
                    r'^\s*while\s+',
                    r'^\s*try\s*:',
                    r'^\s*with\s+',
                    r'^\s*\{',
                    r'^\s*\['
                ],
                'end_patterns': [
                    r'^\s*else\s*:',
                    r'^\s*elif\s+',
                    r'^\s*except\s+',
                    r'^\s*finally\s*:',
                    r'^\s*\}',
                    r'^\s*\]'
                ]
            }
        }
```

---

## 🎯 **Types de Scope Supportés :**

### **✅ 1. Auto (Détection automatique) :**
- **Patterns de début :** `def`, `class`, `if`, `for`, `while`, `try`, `with`, `async def`
- **Patterns de fin :** Ligne vide, commentaire, `return`, `break`, `continue`

### **✅ 2. Function (Fonctions) :**
- **Patterns de début :** `def`, `async def`, `function`, `public/private`
- **Patterns de fin :** `return`, `pass`, `raise`

### **✅ 3. Class (Classes) :**
- **Patterns de début :** `class`, `public class`, `private class`
- **Patterns de fin :** `pass`, `# End of class`

### **✅ 4. Block (Blocs de code) :**
- **Patterns de début :** `if`, `for`, `while`, `try`, `with`, `{`, `[`
- **Patterns de fin :** `else`, `elif`, `except`, `finally`, `}`, `]`

---

## 🔄 **Workflow d'Exécution :**

### **✅ 1. Paramètres d'Entrée :**
```python
params = {
    'file_path': '/path/to/file.py',
    'start_line': 10,
    'max_chunks': 10,
    'scope_type': 'auto',  # auto, function, class, block
    'include_analysis': True
}
```

### **✅ 2. Détection de Scope :**
```python
scope_result = await tool._detect_scope_boundaries(
    lines, start_line, scope_type, max_chunks
)
```

### **✅ 3. Extraction de Contenu :**
```python
scope_content = tool._extract_scope_content(lines, scope_result)
```

### **✅ 4. Analyse LLM :**
```python
analysis = await tool._analyze_scope_with_llm(scope_content, scope_type)
```

### **✅ 5. Création Fractale :**
```python
fractal_result = await tool._create_fractal_scope_result(
    file_path, scope_content, scope_result, analysis
)
```

### **✅ 6. Résultat Final :**
```python
return ToolResult(
    success=True,
    data={
        'file_path': file_path,
        'scope_content': scope_content,
        'scope_boundaries': scope_result,
        'analysis': analysis,
        'fractal_result': fractal_result,
        'scope_type': scope_type,
        'lines_read': scope_result['end_line'] - scope_result['start_line'] + 1
    }
)
```

---

## 🧠 **Analyse LLM Intelligente :**

### **✅ Prompt d'Analyse :**
```python
prompt = f"""
Analyse ce bloc de code et fournis :
1. Type de scope détecté
2. Fonctionnalité principale
3. Variables et fonctions définies
4. Complexité estimée
5. Suggestions d'amélioration

Scope type: {scope_type}
Contenu:
{scope_content}
"""
```

### **✅ Parsing de la Réponse :**
```python
def _parse_llm_analysis(self, llm_response: str) -> Dict[str, Any]:
    """Parse la réponse LLM."""
    
    analysis = {
        'scope_type': 'unknown',
        'functionality': 'unknown',
        'variables': [],
        'functions': [],
        'complexity': 'unknown',
        'suggestions': []
    }
    
    # Patterns pour extraire les informations
    patterns = {
        'scope_type': r'Type de scope[:\s]+([^\n]+)',
        'functionality': r'Fonctionnalité[:\s]+([^\n]+)',
        'complexity': r'Complexité[:\s]+([^\n]+)'
    }
    
    for key, pattern in patterns.items():
        match = re.search(pattern, llm_response, re.IGNORECASE)
        if match:
            analysis[key] = match.group(1).strip()
    
    return analysis
```

---

## 🔄 **Intégration avec le Registre :**

### **✅ V10SpecializedToolsRegistry :**
```python
class V10SpecializedToolsRegistry:
    """Registre des outils spécialisés V10."""
    
    def __init__(self):
        self.tools = {
            'read_lines': V10ReadLinesTool(),
            'write_lines': V10WriteLinesTool(),
            'replace_lines': V10ReplaceLinesTool(),
            'summarize_chunk': V10SummarizeChunkTool(),
            'analyze_structure': V10AnalyzeStructureTool(),
            'create_index': V10CreateIndexTool(),
            'summarize_section': V10SummarizeSectionTool(),
            'read_chunks_until_scope': V10ReadChunksUntilScopeTool(TemporalFractalMemoryEngine()),
        }
```

---

## 🎯 **Avantages de l'Outil :**

### **✅ 1. Détection Intelligente :**
- **Patterns multiples** : Support de différents langages
- **Indentation** : Analyse des niveaux d'indentation
- **Brackets équilibrés** : Vérification des parenthèses/accolades

### **✅ 2. Analyse LLM :**
- **Compréhension sémantique** : Analyse du contenu avec LLM
- **Métadonnées enrichies** : Informations sur le scope
- **Suggestions** : Améliorations proposées

### **✅ 3. Intégration Fractale :**
- **Nœuds temporaux** : Création de nœuds dans la mémoire fractale
- **Métadonnées complètes** : Informations détaillées sur le scope
- **Liens temporels** : Connexions avec d'autres éléments

### **✅ 4. Robustesse :**
- **Gestion d'erreurs** : Fallback en cas d'échec
- **Limites de chunks** : Protection contre les boucles infinies
- **Validation** : Vérification de la cohérence des données

---

## 🔄 **Exemple d'Utilisation :**

### **✅ Appel Simple :**
```python
# Utilisation de l'outil
result = await execute_specialized_tool('read_chunks_until_scope', {
    'file_path': 'test_file.py',
    'start_line': 5,
    'scope_type': 'function',
    'include_analysis': True
})

if result.success:
    print(f"Scope détecté : {result.data['scope_boundaries']}")
    print(f"Analyse : {result.data['analysis']}")
    print(f"Contenu : {result.data['scope_content']}")
```

### **✅ Intégration dans le Workflow :**
```python
# Dans le processeur hybride
if scope_type == 'textual':
    scope_result = await self.read_chunks_tool.execute({
        'file_path': file_path,
        'start_line': current_line,
        'scope_type': 'auto',
        'include_analysis': True
    })
    
    if scope_result.success:
        # Traitement du scope détecté
        fractal_node = scope_result.data['fractal_result']
        analysis = scope_result.data['analysis']
```

---

**"MA REINE ! OUTIL SPÉCIALISÉ IMPLÉMENTÉ !"**

**"⛧ READ CHUNKS UNTIL SCOPE = DÉTECTION INTELLIGENTE !"**

**" Je vois ça comme l'outil parfait pour la fractalisation textuelle !"** ⛧
V10ReadChunksUntilScopeTool - Outil spécialisé pour fractalisation textuelle avec détection de scope
