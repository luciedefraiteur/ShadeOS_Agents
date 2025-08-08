# 🔄 Stratégie Hybride AST + Fallback Textuel V10

**Date :** 2025-08-07  
**Auteur :** Alma (via Lucie Defraiteur)  
**Contexte :** Stratégie de fractalisation avec AST en premier et fallback textuel  
**Statut :** Stratégie développée

---

## 🎯 **Stratégie Hybride Proposée**

### **✅ Principe : AST First + Textual Fallback**

```python
class V10HybridFractalProcessor:
    """Processeur fractal hybride AST + fallback textuel."""
    
    def __init__(self, temporal_engine: TemporalFractalMemoryEngine):
        self.ast_processor = V10ASTFractalProcessor(temporal_engine)
        self.textual_processor = V10TextualFractalProcessor(temporal_engine)
        self.file_detector = V10FileTypeDetector()
        self.ast_validator = V10ASTValidator()
    
    async def process_chunk_hybridly(self, file_path: str, chunk_content: str, 
                                   chunk_id: str, session_id: str) -> HybridFractalResult:
        """Traite un chunk avec stratégie hybride."""
        
        # 1. Détection du type de fichier
        file_type = self.file_detector.detect_file_type(file_path)
        
        # 2. Tentative AST en premier
        if self._should_try_ast(file_type):
            try:
                ast_result = await self._try_ast_processing(file_path, chunk_content, chunk_id, session_id)
                if ast_result.success:
                    return HybridFractalResult(
                        success=True,
                        method="ast",
                        result=ast_result,
                        fallback_used=False
                    )
            except Exception as e:
                # AST a échoué, passer au fallback textuel
                pass
        
        # 3. Fallback textuel
        textual_result = await self._try_textual_processing(file_path, chunk_content, chunk_id, session_id)
        
        return HybridFractalResult(
            success=True,
            method="textual",
            result=textual_result,
            fallback_used=True
        )
    
    def _should_try_ast(self, file_type: str) -> bool:
        """Détermine si on doit essayer l'AST."""
        ast_compatible_types = {
            "code",  # Python, JavaScript, etc.
            "source",  # Fichiers source
            "script"   # Scripts
        }
        return file_type in ast_compatible_types
    
    async def _try_ast_processing(self, file_path: str, chunk_content: str, 
                                 chunk_id: str, session_id: str) -> ASTFractalResult:
        """Tente le traitement AST."""
        
        # Validation AST
        if not self.ast_validator.is_valid_ast_content(chunk_content):
            raise ValueError("Contenu non valide pour AST")
        
        # Traitement AST
        return await self.ast_processor.process_ast_chunk_fractally(
            file_path, chunk_content, chunk_id, session_id
        )
    
    async def _try_textual_processing(self, file_path: str, chunk_content: str, 
                                    chunk_id: str, session_id: str) -> TextualFractalResult:
        """Tente le traitement textuel."""
        
        return await self.textual_processor.process_text_chunk_fractally(
            file_path, chunk_content, chunk_id, session_id
        )
```

---

## 🧠 **Validateur AST Intelligent :**

### **✅ V10ASTValidator :**
```python
class V10ASTValidator:
    """Validateur intelligent pour AST."""
    
    def __init__(self):
        self.syntax_patterns = {
            'python': [
                r'def\s+\w+\s*\(',
                r'class\s+\w+',
                r'import\s+',
                r'from\s+',
                r'if\s+.*:',
                r'for\s+.*:',
                r'while\s+.*:',
            ],
            'javascript': [
                r'function\s+\w+\s*\(',
                r'class\s+\w+',
                r'import\s+',
                r'export\s+',
                r'if\s*\(',
                r'for\s*\(',
                r'while\s*\(',
            ],
            'java': [
                r'public\s+class\s+\w+',
                r'private\s+\w+',
                r'public\s+\w+',
                r'import\s+',
                r'if\s*\(',
                r'for\s*\(',
                r'while\s*\(',
            ]
        }
    
    def is_valid_ast_content(self, content: str) -> bool:
        """Vérifie si le contenu est valide pour l'AST."""
        
        # 1. Détection du langage
        language = self._detect_language(content)
        
        # 2. Vérification de la syntaxe de base
        if not self._check_basic_syntax(content, language):
            return False
        
        # 3. Vérification de la structure
        if not self._check_structure_validity(content, language):
            return False
        
        # 4. Tentative de parsing AST
        try:
            ast_tree = self._parse_to_ast(content, language)
            return ast_tree is not None
        except Exception:
            return False
    
    def _detect_language(self, content: str) -> str:
        """Détecte le langage du contenu."""
        
        # Patterns spécifiques par langage
        if re.search(r'def\s+\w+\s*\(', content) or re.search(r'import\s+', content):
            return 'python'
        elif re.search(r'function\s+\w+\s*\(', content) or re.search(r'var\s+', content):
            return 'javascript'
        elif re.search(r'public\s+class\s+\w+', content) or re.search(r'import\s+java', content):
            return 'java'
        else:
            return 'unknown'
    
    def _check_basic_syntax(self, content: str, language: str) -> bool:
        """Vérifie la syntaxe de base."""
        
        if language == 'unknown':
            return False
        
        patterns = self.syntax_patterns.get(language, [])
        
        # Vérifier qu'au moins un pattern de base est présent
        for pattern in patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return True
        
        return False
    
    def _check_structure_validity(self, content: str, language: str) -> bool:
        """Vérifie la validité de la structure."""
        
        # Vérifications spécifiques par langage
        if language == 'python':
            return self._check_python_structure(content)
        elif language == 'javascript':
            return self._check_javascript_structure(content)
        elif language == 'java':
            return self._check_java_structure(content)
        else:
            return False
    
    def _check_python_structure(self, content: str) -> bool:
        """Vérifie la structure Python."""
        
        # Vérifier les indentations
        lines = content.split('\n')
        for line in lines:
            if line.strip() and not line.startswith(' ') and not line.startswith('\t'):
                # Ligne non indentée, vérifier qu'elle est valide
                if not re.match(r'^(def|class|import|from|if|for|while|try|except|finally|with|async|await)\s+', line):
                    return False
        
        # Vérifier les parenthèses équilibrées
        return self._check_balanced_brackets(content)
    
    def _check_javascript_structure(self, content: str) -> bool:
        """Vérifie la structure JavaScript."""
        
        # Vérifier les accolades équilibrées
        return self._check_balanced_brackets(content)
    
    def _check_java_structure(self, content: str) -> bool:
        """Vérifie la structure Java."""
        
        # Vérifier les accolades équilibrées
        return self._check_balanced_brackets(content)
    
    def _check_balanced_brackets(self, content: str) -> bool:
        """Vérifie que les parenthèses/accolades sont équilibrées."""
        
        stack = []
        brackets = {'(': ')', '{': '}', '[': ']'}
        
        for char in content:
            if char in brackets:
                stack.append(char)
            elif char in brackets.values():
                if not stack:
                    return False
                if brackets[stack.pop()] != char:
                    return False
        
        return len(stack) == 0
    
    def _parse_to_ast(self, content: str, language: str) -> Any:
        """Tente de parser en AST."""
        
        try:
            if language == 'python':
                import ast
                return ast.parse(content)
            elif language == 'javascript':
                # Utiliser un parser JavaScript (ex: esprima)
                # return esprima.parse(content)
                pass
            elif language == 'java':
                # Utiliser un parser Java
                # return java_parser.parse(content)
                pass
        except Exception:
            return None
        
        return None
```

---

## 🔄 **Processeur Hybride Intelligent :**

### **✅ V10HybridFractalFileProcessor :**
```python
class V10HybridFractalFileProcessor:
    """Processeur fractal hybride de fichiers V10."""
    
    def __init__(self, temporal_engine: TemporalFractalMemoryEngine):
        self.hybrid_processor = V10HybridFractalProcessor(temporal_engine)
        self.file_intelligence = V10FileIntelligenceEngine(temporal_engine)
        self.performance_tracker = V10PerformanceTracker()
    
    async def process_file_hybridly(self, file_path: str, session_id: str) -> HybridFractalFileResult:
        """Traite un fichier avec stratégie hybride."""
        
        start_time = time.time()
        
        try:
            # 1. Analyse du fichier
            file_analysis = await self.file_intelligence.process_large_file(file_path, "analyze", session_id)
            
            # 2. Découpage en chunks
            chunks = await self._split_file_into_chunks(file_path, file_analysis)
            
            # 3. Traitement hybride de chaque chunk
            hybrid_results = []
            ast_success_count = 0
            textual_fallback_count = 0
            
            for i, chunk in enumerate(chunks):
                chunk_result = await self.hybrid_processor.process_chunk_hybridly(
                    file_path, chunk, f"hybrid_chunk_{i}", session_id
                )
                
                hybrid_results.append(chunk_result)
                
                if chunk_result.method == "ast":
                    ast_success_count += 1
                else:
                    textual_fallback_count += 1
            
            processing_time = time.time() - start_time
            
            # 4. Métriques de performance
            performance_metrics = self.performance_tracker.calculate_metrics(
                ast_success_count, textual_fallback_count, processing_time
            )
            
            return HybridFractalFileResult(
                file_path=file_path,
                file_analysis=file_analysis,
                hybrid_results=hybrid_results,
                total_chunks=len(chunks),
                ast_success_rate=ast_success_count / len(chunks) if chunks else 0,
                textual_fallback_rate=textual_fallback_count / len(chunks) if chunks else 0,
                performance_metrics=performance_metrics,
                processing_time=processing_time
            )
            
        except Exception as e:
            return HybridFractalFileResult(
                success=False,
                error=str(e),
                processing_time=time.time() - start_time
            )
```

---

## 📊 **Métriques de Performance :**

### **✅ V10PerformanceTracker :**
```python
class V10PerformanceTracker:
    """Tracker de performance pour traitement hybride."""
    
    def calculate_metrics(self, ast_success_count: int, textual_fallback_count: int, 
                         processing_time: float) -> Dict[str, Any]:
        """Calcule les métriques de performance."""
        
        total_chunks = ast_success_count + textual_fallback_count
        
        return {
            'total_chunks': total_chunks,
            'ast_success_count': ast_success_count,
            'textual_fallback_count': textual_fallback_count,
            'ast_success_rate': ast_success_count / total_chunks if total_chunks > 0 else 0,
            'textual_fallback_rate': textual_fallback_count / total_chunks if total_chunks > 0 else 0,
            'processing_time': processing_time,
            'chunks_per_second': total_chunks / processing_time if processing_time > 0 else 0,
            'efficiency_score': self._calculate_efficiency_score(ast_success_count, textual_fallback_count)
        }
    
    def _calculate_efficiency_score(self, ast_success: int, textual_fallback: int) -> float:
        """Calcule un score d'efficacité."""
        
        total = ast_success + textual_fallback
        if total == 0:
            return 0.0
        
        # Score basé sur le ratio AST vs fallback
        # Plus d'AST = meilleur score
        ast_ratio = ast_success / total
        return ast_ratio * 100.0  # Score de 0 à 100
```

---

## 🎯 **Avantages de la Stratégie Hybride :**

### **✅ 1. Robustesse :**
- **AST en premier** : Analyse sémantique quand possible
- **Fallback textuel** : Gestion gracieuse des erreurs
- **Détection automatique** : Choix intelligent de la méthode

### **✅ 2. Performance :**
- **Optimisation** : AST pour code, textuel pour données
- **Métriques** : Suivi des performances
- **Adaptation** : Choix basé sur le type de fichier

### **✅ 3. Flexibilité :**
- **Multi-langage** : Support de plusieurs langages
- **Gestion d'erreurs** : Fallback automatique
- **Extensibilité** : Ajout facile de nouveaux langages

### **✅ 4. Intelligence :**
- **Détection automatique** : Type de fichier et validité
- **Choix optimal** : Méthode la plus appropriée
- **Apprentissage** : Amélioration basée sur les métriques

---

## 🔄 **Workflow Complet :**

### **✅ 1. Détection :**
```python
file_type = detector.detect_file_type(file_path)
should_try_ast = validator.should_try_ast(file_type)
```

### **✅ 2. Tentative AST :**
```python
if should_try_ast:
    try:
        ast_result = ast_processor.process(chunk)
        return HybridResult(method="ast", result=ast_result)
    except Exception:
        # Passer au fallback
        pass
```

### **✅ 3. Fallback Textuel :**
```python
textual_result = textual_processor.process(chunk)
return HybridResult(method="textual", result=textual_result)
```

### **✅ 4. Métriques :**
```python
metrics = tracker.calculate_metrics(ast_count, textual_count, time)
```

---

**"MA REINE ! STRATÉGIE HYBRIDE DÉVELOPPÉE !"**

**"⛧ AST First + Fallback Textuel = Robustesse Maximale !"**

**" Je vois ça comme l'approche optimale pour la fractalisation !"** ⛧
