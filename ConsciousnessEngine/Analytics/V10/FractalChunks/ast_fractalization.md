# 🌳 Fractalisation AST Parser des Chunks V10

**Date :** 2025-08-07  
**Auteur :** Alma (via Lucie Defraiteur)  
**Contexte :** Fractalisation basée sur l'AST Parser pour chunks de code  
**Statut :** Concept développé

---

## 🎯 **Concept de Fractalisation AST Parser**

### **✅ Hiérarchie AST Fractale :**

#### **1. Niveau File (Racine) :**
```python
@dataclass
class ASTFileFractalNode:
    """Nœud fractal AST de fichier."""
    file_id: str
    file_path: str
    file_size: int
    language: str
    ast_summary: str
    created_at: datetime
    modules: List['ASTModuleFractalNode']
    ast_metadata: Dict[str, Any]
```

#### **2. Niveau Module (Branche) :**
```python
@dataclass
class ASTModuleFractalNode:
    """Nœud fractal AST de module."""
    module_id: str
    module_name: str
    imports: List['ASTImportFractalNode']
    classes: List['ASTClassFractalNode']
    functions: List['ASTFunctionFractalNode']
    variables: List['ASTVariableFractalNode']
    parent_file_id: str
```

#### **3. Niveau Class (Feuille) :**
```python
@dataclass
class ASTClassFractalNode:
    """Nœud fractal AST de classe."""
    class_id: str
    class_name: str
    base_classes: List[str]
    methods: List['ASTMethodFractalNode']
    attributes: List['ASTAttributeFractalNode']
    decorators: List['ASTDecoratorFractalNode']
    parent_module_id: str
    complexity_score: float
```

#### **4. Niveau Function/Method (Micro) :**
```python
@dataclass
class ASTFunctionFractalNode:
    """Nœud fractal AST de fonction."""
    function_id: str
    function_name: str
    parameters: List['ASTParameterFractalNode']
    return_type: str
    body: List['ASTStatementFractalNode']
    decorators: List['ASTDecoratorFractalNode']
    parent_class_id: str
    complexity_score: float
```

#### **5. Niveau Statement (Nano) :**
```python
@dataclass
class ASTStatementFractalNode:
    """Nœud fractal AST de statement."""
    statement_id: str
    statement_type: str  # if, for, while, return, assignment, etc.
    statement_content: str
    line_number: int
    expressions: List['ASTExpressionFractalNode']
    parent_function_id: str
```

#### **6. Niveau Expression (Pico) :**
```python
@dataclass
class ASTExpressionFractalNode:
    """Nœud fractal AST d'expression."""
    expression_id: str
    expression_type: str  # binary_op, unary_op, call, attribute, etc.
    expression_value: str
    operands: List['ASTOperandFractalNode']
    parent_statement_id: str
```

---

## 🧠 **Processeur AST Fractal :**

### **✅ V10ASTFractalProcessor :**
```python
class V10ASTFractalProcessor:
    """Processeur fractal AST pour chunks de code avec mémoire temporelle."""
    
    def __init__(self, temporal_engine: TemporalFractalMemoryEngine):
        self.temporal_engine = temporal_engine
        self.ast_parser = V10ASTParser()
        self.code_analyzer = V10CodeAnalyzer()
    
    async def process_ast_chunk_fractally(self, file_path: str, chunk_content: str, 
                                        chunk_id: str, session_id: str) -> ASTFractalResult:
        """Traite un chunk de code de manière fractale avec AST."""
        
        # 1. Parser l'AST du chunk
        ast_tree = await self.ast_parser.parse_code_to_ast(chunk_content)
        
        # 2. Créer le nœud chunk AST fractal
        chunk_node = await self._create_ast_chunk_fractal_node(ast_tree, chunk_id)
        
        # 3. Analyser la structure AST fractale
        ast_structure = await self._analyze_ast_fractal_structure(ast_tree)
        
        # 4. Créer les nœuds enfants (classes, fonctions)
        class_nodes = await self._create_class_fractal_nodes(ast_tree, chunk_id)
        function_nodes = await self._create_function_fractal_nodes(ast_tree, chunk_id)
        
        # 5. Créer les nœuds statements
        statement_nodes = await self._create_statement_fractal_nodes(function_nodes)
        
        # 6. Créer les nœuds expressions
        expression_nodes = await self._create_expression_fractal_nodes(statement_nodes)
        
        # 7. Enregistrer dans la mémoire temporelle
        await self._register_ast_fractal_hierarchy(chunk_node, class_nodes, function_nodes, 
                                                 statement_nodes, expression_nodes, session_id)
        
        return ASTFractalResult(
            chunk_node=chunk_node,
            ast_structure=ast_structure,
            class_count=len(class_nodes),
            function_count=len(function_nodes),
            statement_count=sum(len(statements) for statements in statement_nodes.values()),
            expression_count=sum(len(expressions) for expressions in expression_nodes.values())
        )
    
    async def _create_ast_chunk_fractal_node(self, ast_tree: Any, chunk_id: str) -> ASTChunkFractalNode:
        """Crée un nœud fractal AST de chunk."""
        
        # Analyse AST intelligente
        ast_summary = await self.code_analyzer.summarize_ast_content(ast_tree)
        
        # Analyse structurelle AST
        ast_analysis = self.code_analyzer._analyze_ast_structure(ast_tree)
        key_elements = self.code_analyzer._extract_key_ast_elements(ast_tree, ast_analysis)
        
        return ASTChunkFractalNode(
            chunk_id=chunk_id,
            ast_tree=ast_tree,
            ast_summary=ast_summary,
            classes=[],  # Sera rempli plus tard
            functions=[],  # Sera rempli plus tard
            key_elements=key_elements,
            complexity_score=self.code_analyzer._calculate_ast_complexity(ast_tree),
            parent_module_id=None,  # Sera défini plus tard
            processing_time=0.0
        )
    
    async def _analyze_ast_fractal_structure(self, ast_tree: Any) -> Dict[str, Any]:
        """Analyse la structure AST fractale."""
        
        ast_structure = {
            'total_nodes': 0,
            'class_count': 0,
            'function_count': 0,
            'statement_count': 0,
            'expression_count': 0,
            'node_types': {},
            'complexity_metrics': {},
            'dependencies': {}
        }
        
        # Parcourir l'AST et compter les éléments
        await self._traverse_ast_and_count(ast_tree, ast_structure)
        
        return ast_structure
    
    async def _traverse_ast_and_count(self, node: Any, structure: Dict[str, Any]):
        """Parcourt l'AST et compte les éléments."""
        if hasattr(node, 'type'):
            structure['total_nodes'] += 1
            node_type = node.type
            structure['node_types'][node_type] = structure['node_types'].get(node_type, 0) + 1
            
            # Compter les éléments spécifiques
            if node_type == 'ClassDef':
                structure['class_count'] += 1
            elif node_type == 'FunctionDef':
                structure['function_count'] += 1
            elif node_type in ['If', 'For', 'While', 'Return', 'Assign']:
                structure['statement_count'] += 1
            elif node_type in ['BinOp', 'UnaryOp', 'Call', 'Attribute']:
                structure['expression_count'] += 1
        
        # Parcourir les enfants
        for child in getattr(node, 'body', []):
            await self._traverse_ast_and_count(child, structure)
    
    async def _create_class_fractal_nodes(self, ast_tree: Any, chunk_id: str) -> List[ASTClassFractalNode]:
        """Crée les nœuds fractals AST de classes."""
        
        class_nodes = []
        
        for node in ast_tree.body:
            if hasattr(node, 'type') and node.type == 'ClassDef':
                class_node = ASTClassFractalNode(
                    class_id=f"{chunk_id}_class_{len(class_nodes)}",
                    class_name=node.name,
                    base_classes=[base.id for base in node.bases],
                    methods=[],
                    attributes=[],
                    decorators=[],
                    parent_module_id=chunk_id,
                    complexity_score=self.code_analyzer._calculate_class_complexity(node)
                )
                
                # Extraire les méthodes
                for child in node.body:
                    if hasattr(child, 'type') and child.type == 'FunctionDef':
                        method_node = await self._create_method_fractal_node(child, class_node.class_id)
                        class_node.methods.append(method_node)
                
                class_nodes.append(class_node)
        
        return class_nodes
    
    async def _create_function_fractal_nodes(self, ast_tree: Any, chunk_id: str) -> List[ASTFunctionFractalNode]:
        """Crée les nœuds fractals AST de fonctions."""
        
        function_nodes = []
        
        for node in ast_tree.body:
            if hasattr(node, 'type') and node.type == 'FunctionDef':
                function_node = ASTFunctionFractalNode(
                    function_id=f"{chunk_id}_function_{len(function_nodes)}",
                    function_name=node.name,
                    parameters=[],
                    return_type="Any",  # À améliorer avec type hints
                    body=[],
                    decorators=[],
                    parent_class_id=None,  # Sera défini plus tard
                    complexity_score=self.code_analyzer._calculate_function_complexity(node)
                )
                
                # Extraire les paramètres
                for arg in node.args.args:
                    param_node = ASTParameterFractalNode(
                        parameter_id=f"{function_node.function_id}_param_{len(function_node.parameters)}",
                        parameter_name=arg.arg,
                        parameter_type="Any",  # À améliorer
                        default_value=None,
                        parent_function_id=function_node.function_id
                    )
                    function_node.parameters.append(param_node)
                
                # Extraire les statements du body
                for child in node.body:
                    if hasattr(child, 'type'):
                        statement_node = await self._create_statement_fractal_node(child, function_node.function_id)
                        function_node.body.append(statement_node)
                
                function_nodes.append(function_node)
        
        return function_nodes
    
    async def _create_statement_fractal_nodes(self, function_nodes: List[ASTFunctionFractalNode]) -> Dict[str, List[ASTStatementFractalNode]]:
        """Crée les nœuds fractals AST de statements."""
        
        statement_nodes = {}
        
        for function_node in function_nodes:
            function_statements = []
            
            for statement in function_node.body:
                if hasattr(statement, 'type'):
                    statement_node = ASTStatementFractalNode(
                        statement_id=f"{function_node.function_id}_stmt_{len(function_statements)}",
                        statement_type=statement.type,
                        statement_content=str(statement),
                        line_number=getattr(statement, 'lineno', 0),
                        expressions=[],
                        parent_function_id=function_node.function_id
                    )
                    
                    # Extraire les expressions du statement
                    for child in self._get_statement_children(statement):
                        if hasattr(child, 'type'):
                            expression_node = await self._create_expression_fractal_node(child, statement_node.statement_id)
                            statement_node.expressions.append(expression_node)
                    
                    function_statements.append(statement_node)
            
            statement_nodes[function_node.function_id] = function_statements
        
        return statement_nodes
    
    async def _create_expression_fractal_nodes(self, statement_nodes: Dict[str, List[ASTStatementFractalNode]]) -> Dict[str, List[ASTExpressionFractalNode]]:
        """Crée les nœuds fractals AST d'expressions."""
        
        expression_nodes = {}
        
        for function_id, statements in statement_nodes.items():
            for statement in statements:
                statement_expressions = []
                
                for expression in statement.expressions:
                    expression_node = ASTExpressionFractalNode(
                        expression_id=f"{statement.statement_id}_expr_{len(statement_expressions)}",
                        expression_type=expression.type,
                        expression_value=str(expression),
                        operands=[],
                        parent_statement_id=statement.statement_id
                    )
                    
                    # Extraire les opérandes
                    for child in self._get_expression_children(expression):
                        operand_node = ASTOperandFractalNode(
                            operand_id=f"{expression_node.expression_id}_op_{len(expression_node.operands)}",
                            operand_value=str(child),
                            operand_type=child.type if hasattr(child, 'type') else 'unknown',
                            parent_expression_id=expression_node.expression_id
                        )
                        expression_node.operands.append(operand_node)
                    
                    statement_expressions.append(expression_node)
                
                expression_nodes[statement.statement_id] = statement_expressions
        
        return expression_nodes
    
    def _get_statement_children(self, statement: Any) -> List[Any]:
        """Récupère les enfants d'un statement."""
        children = []
        
        if hasattr(statement, 'body'):
            children.extend(statement.body)
        if hasattr(statement, 'test'):
            children.append(statement.test)
        if hasattr(statement, 'value'):
            children.append(statement.value)
        
        return children
    
    def _get_expression_children(self, expression: Any) -> List[Any]:
        """Récupère les enfants d'une expression."""
        children = []
        
        if hasattr(expression, 'left'):
            children.append(expression.left)
        if hasattr(expression, 'right'):
            children.append(expression.right)
        if hasattr(expression, 'operand'):
            children.append(expression.operand)
        if hasattr(expression, 'args'):
            children.extend(expression.args)
        if hasattr(expression, 'value'):
            children.append(expression.value)
        
        return children
```

---

## 📊 **Avantages de la Fractalisation AST :**

### **✅ 1. Navigation AST Hiérarchique :**
- **File → Module → Class → Function → Statement → Expression**
- **Navigation contextuelle** basée sur la structure du code
- **Zoom in/out** sur les niveaux de détail AST

### **✅ 2. Recherche AST Fractale :**
- **Recherche par niveau** : expressions, statements, fonctions, classes
- **Recherche contextuelle** : selon la hiérarchie AST
- **Recherche temporelle** : évolution du code dans le temps

### **✅ 3. Analyse de Complexité :**
- **Complexité cyclomatique** par niveau
- **Métriques de qualité** du code
- **Détection de patterns** et anti-patterns

### **✅ 4. Mémoire Temporelle AST :**
- **Liens temporels** entre niveaux AST
- **Évolution fractale** du code dans le temps
- **Contexte AST persistant** pour l'IA

---

## 🎯 **Intégration avec V10 :**

### **✅ V10ASTFractalFileProcessor :**
```python
class V10ASTFractalFileProcessor:
    """Processeur fractal AST de fichiers V10."""
    
    def __init__(self, temporal_engine: TemporalFractalMemoryEngine):
        self.ast_fractal_processor = V10ASTFractalProcessor(temporal_engine)
        self.file_intelligence = V10FileIntelligenceEngine(temporal_engine)
    
    async def process_ast_file_fractally(self, file_path: str, session_id: str) -> ASTFractalFileResult:
        """Traite un fichier de code de manière fractale avec AST."""
        
        # 1. Analyse du fichier de code
        file_analysis = await self.file_intelligence.process_large_file(file_path, "analyze", session_id)
        
        # 2. Découpage en chunks de code
        code_chunks = await self._split_code_file_into_chunks(file_path, file_analysis)
        
        # 3. Traitement fractal AST de chaque chunk
        ast_fractal_results = []
        for i, chunk in enumerate(code_chunks):
            chunk_result = await self.ast_fractal_processor.process_ast_chunk_fractally(
                file_path, chunk, f"ast_chunk_{i}", session_id
            )
            ast_fractal_results.append(chunk_result)
        
        return ASTFractalFileResult(
            file_path=file_path,
            file_analysis=file_analysis,
            ast_fractal_results=ast_fractal_results,
            total_ast_chunks=len(code_chunks)
        )
```

---

## 🔄 **Comparaison Textuel vs AST :**

### **✅ Fractalisation Textuelle :**
- **Avantages** : Simple, rapide, universel
- **Inconvénients** : Pas de compréhension sémantique
- **Usage** : Documents, logs, données textuelles

### **✅ Fractalisation AST :**
- **Avantages** : Compréhension sémantique, analyse de complexité
- **Inconvénients** : Plus complexe, spécifique au langage
- **Usage** : Code source, analyse de qualité

---

**Rapport généré automatiquement par Alma**  
**Date :** 2025-08-07  
**Statut :** Concept de fractalisation AST développé
