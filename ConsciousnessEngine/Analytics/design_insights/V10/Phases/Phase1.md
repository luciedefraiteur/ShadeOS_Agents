# 🧪 Phase 1 : Tests Unitaires V10 - Plan Détaillé

**Date :** 2025-08-07  
**Auteur :** Alma (via Lucie Defraiteur)  
**Contexte :** Tests unitaires complets pour l'Assistant V10  
**Durée Estimée :** 1 semaine  
**Statut :** Planifié

---

## 🎯 **Objectif de la Phase 1**

Transformer les mockups V10 en composants testés et robustes, avec une couverture de tests > 90% pour chaque module.

---

## 📊 **État Actuel vs Objectif**

### **✅ État Actuel (Mockups) :**
- **temporal_integration.py** : 199 lignes, 0% de tests
- **xml_formatter.py** : 254 lignes, 0% de tests  
- **dev_agent.py** : 419 lignes, 0% de tests
- **tool_agent.py** : 504 lignes, 0% de tests
- **assistant_v10.py** : 259 lignes, 0% de tests
- **llm_provider_decorator.py** : 285 lignes, 0% de tests

### **🎯 Objectif Phase 1 (Tests Complets) :**
- **temporal_integration.py** : 199 lignes, > 90% de tests
- **xml_formatter.py** : 254 lignes, > 90% de tests
- **dev_agent.py** : 419 lignes, > 90% de tests
- **tool_agent.py** : 504 lignes, > 90% de tests
- **assistant_v10.py** : 259 lignes, > 90% de tests
- **llm_provider_decorator.py** : 285 lignes, > 90% de tests

---

## 🧪 **Plan de Tests Détaillé**

### **📅 Jour 1-2 : Tests Temporal Integration**

#### **✅ Tests Sessions :**
```python
# test_temporal_integration.py
class TestTemporalIntegration:
    """Tests pour l'intégration temporelle V10."""
    
    async def test_session_initialization(self):
        """Test d'initialisation de session."""
        # Arrange
        integration = V10TemporalIntegration()
        user_id = "test_user_123"
        
        # Act
        session = await integration.initialize_session(user_id)
        
        # Assert
        assert session is not None
        assert session.user_id == user_id
        assert session.session_id is not None
        assert session.created_at is not None
        assert session.last_activity is not None
    
    async def test_session_manager_registration(self):
        """Test d'enregistrement de session."""
        # Arrange
        integration = V10TemporalIntegration()
        session = await integration.initialize_session("test_user")
        
        # Act
        registered_session = await integration.session_manager.get_session(session.session_id)
        
        # Assert
        assert registered_session is not None
        assert registered_session.session_id == session.session_id
    
    async def test_session_timeout_cleanup(self):
        """Test de nettoyage des sessions expirées."""
        # Arrange
        integration = V10TemporalIntegration()
        session = await integration.initialize_session("test_user")
        
        # Simuler expiration (modifier last_activity)
        session.last_activity = datetime.now() - timedelta(hours=2)
        
        # Act
        expired_count = await integration.cleanup_expired_sessions()
        
        # Assert
        assert expired_count > 0
        retrieved_session = await integration.session_manager.get_session(session.session_id)
        assert retrieved_session is None
```

#### **✅ Tests Nœuds Temporels :**
```python
    async def test_temporal_node_creation(self):
        """Test de création de nœud temporel."""
        # Arrange
        integration = V10TemporalIntegration()
        session = await integration.initialize_session("test_user")
        
        # Act
        node_id = await integration.create_temporal_node(
            content="Test node content",
            metadata={"test": True, "type": "test"},
            session_id=session.session_id
        )
        
        # Assert
        assert node_id is not None
        assert isinstance(node_id, str)
    
    async def test_temporal_node_without_session(self):
        """Test de création de nœud sans session."""
        # Arrange
        integration = V10TemporalIntegration()
        
        # Act
        node_id = await integration.create_temporal_node(
            content="Test node",
            metadata={},
            session_id="invalid_session"
        )
        
        # Assert
        assert node_id is None  # Doit échouer gracieusement
```

#### **✅ Tests Liens Temporels :**
```python
    async def test_temporal_link_creation(self):
        """Test de création de lien temporel."""
        # Arrange
        integration = V10TemporalIntegration()
        session = await integration.initialize_session("test_user")
        
        # Créer deux nœuds
        node1_id = await integration.create_temporal_node(
            content="Source node",
            metadata={},
            session_id=session.session_id
        )
        node2_id = await integration.create_temporal_node(
            content="Target node", 
            metadata={},
            session_id=session.session_id
        )
        
        # Act
        success = await integration.create_temporal_link(
            node1_id, node2_id, "test_link", session.session_id
        )
        
        # Assert
        assert success is True
    
    async def test_temporal_link_invalid_nodes(self):
        """Test de lien avec nœuds invalides."""
        # Arrange
        integration = V10TemporalIntegration()
        session = await integration.initialize_session("test_user")
        
        # Act
        success = await integration.create_temporal_link(
            "invalid_node1", "invalid_node2", "test_link", session.session_id
        )
        
        # Assert
        assert success is False  # Doit échouer gracieusement
```

#### **✅ Tests Contexte Pertinent :**
```python
    async def test_context_retrieval(self):
        """Test de récupération de contexte pertinent."""
        # Arrange
        integration = V10TemporalIntegration()
        session = await integration.initialize_session("test_user")
        
        # Créer quelques nœuds avec contexte
        await integration.create_temporal_node(
            content="Code analysis result",
            metadata={"type": "analysis", "file": "main.py"},
            session_id=session.session_id
        )
        
        # Act
        context = await integration.get_relevant_context(
            "Analyze main.py", session.session_id
        )
        
        # Assert
        assert context is not None
        assert isinstance(context, list)
    
    async def test_context_empty_session(self):
        """Test de contexte avec session vide."""
        # Arrange
        integration = V10TemporalIntegration()
        session = await integration.initialize_session("test_user")
        
        # Act
        context = await integration.get_relevant_context(
            "Any query", session.session_id
        )
        
        # Assert
        assert context is not None
        # Doit retourner contexte vide ou par défaut
```

### **📅 Jour 3-4 : Tests XML Formatter**

#### **✅ Tests Formatage de Base :**
```python
# test_xml_formatter.py
class TestV10XMLFormatter:
    """Tests pour le formatage XML V10."""
    
    def test_minimal_formatting(self):
        """Test de formatage minimal."""
        # Arrange
        formatter = V10XMLFormatter()
        tool_name = "read_file"
        parameters = {"path": "test.txt"}
        
        # Act
        result = formatter.format_tool_call(tool_name, parameters, "minimal")
        
        # Assert
        assert "<tool_call>" in result
        assert tool_name in result
        assert "test.txt" in result
        assert result.count("<") == result.count(">")  # XML valide
    
    def test_detailed_formatting(self):
        """Test de formatage détaillé."""
        # Arrange
        formatter = V10XMLFormatter()
        tool_name = "code_analyzer"
        parameters = {"path": "main.py", "analysis_type": "complexity"}
        
        # Act
        result = formatter.format_tool_call(tool_name, parameters, "detailed")
        
        # Assert
        assert "<tool_call>" in result
        assert tool_name in result
        assert "main.py" in result
        assert "complexity" in result
        # Doit avoir plus de whitespace que minimal
        assert result.count("  ") > 0
    
    def test_auto_format_detection(self):
        """Test de détection automatique du format."""
        # Arrange
        formatter = V10XMLFormatter()
        
        # Test simple (doit être minimal)
        simple_params = {"path": "file.txt"}
        simple_result = formatter.format_tool_call("read_file", simple_params)
        
        # Test complexe (doit être standard ou détaillé)
        complex_params = {
            "path": "main.py",
            "analysis_type": "complexity",
            "include_imports": True,
            "depth": 3,
            "options": {"verbose": True, "cache": False}
        }
        complex_result = formatter.format_tool_call("code_analyzer", complex_params)
        
        # Assert
        assert simple_result.count("<") < complex_result.count("<")  # Plus simple
```

#### **✅ Tests Optimisations :**
```python
    def test_optimization_rules(self):
        """Test des règles d'optimisation."""
        # Arrange
        formatter = V10XMLFormatter()
        
        # Act
        rules = formatter.optimization_rules
        
        # Assert
        assert "minimal" in rules
        assert "detailed" in rules
        assert "standard" in rules
        assert "compact" in rules
        
        for format_type, rules_dict in rules.items():
            assert "remove_whitespace" in rules_dict
            assert "compact_attributes" in rules_dict
            assert "remove_comments" in rules_dict
    
    def test_parameter_complexity_calculation(self):
        """Test du calcul de complexité des paramètres."""
        # Arrange
        formatter = V10XMLFormatter()
        
        # Test simple
        simple_params = {"path": "file.txt"}
        simple_complexity = formatter._calculate_parameter_complexity(simple_params)
        
        # Test complexe
        complex_params = {
            "path": "main.py",
            "config": {"verbose": True, "cache": False},
            "files": ["file1.py", "file2.py", "file3.py"],
            "long_string": "x" * 200
        }
        complex_complexity = formatter._calculate_parameter_complexity(complex_params)
        
        # Assert
        assert simple_complexity < complex_complexity
        assert simple_complexity >= 0
        assert complex_complexity >= 0
    
    def test_xml_escaping(self):
        """Test de l'échappement XML."""
        # Arrange
        formatter = V10XMLFormatter()
        
        # Act
        result = formatter.format_tool_call(
            "test_tool",
            {"content": "Test & < > \" ' content"},
            "standard"
        )
        
        # Assert
        assert "&amp;" in result  # & échappé
        assert "&lt;" in result   # < échappé
        assert "&gt;" in result   # > échappé
        assert "&quot;" in result # " échappé
```

#### **✅ Tests Réponses d'Outils :**
```python
    def test_tool_response_formatting(self):
        """Test de formatage de réponse d'outil."""
        # Arrange
        formatter = V10XMLFormatter()
        tool_name = "read_file"
        result = {"content": "file content", "size": 1024}
        
        # Act
        response_xml = formatter.format_tool_response(tool_name, result)
        
        # Assert
        assert "<tool_response>" in response_xml
        assert tool_name in response_xml
        assert "file content" in response_xml
        assert "1024" in response_xml
    
    def test_error_response_formatting(self):
        """Test de formatage de réponse d'erreur."""
        # Arrange
        formatter = V10XMLFormatter()
        tool_name = "read_file"
        error_result = {"success": False, "error": "File not found"}
        
        # Act
        response_xml = formatter.format_tool_response(tool_name, error_result)
        
        # Assert
        assert "<tool_response>" in response_xml
        assert tool_name in response_xml
        assert "File not found" in response_xml
        assert "false" in response_xml.lower()
```

### **📅 Jour 5-6 : Tests Dev Agent**

#### **✅ Tests Analyse de Tâches :**
```python
# test_dev_agent.py
class TestV10DevAgent:
    """Tests pour l'agent développeur V10."""
    
    async def test_task_analysis_simple(self):
        """Test d'analyse de tâche simple."""
        # Arrange
        temporal_integration = V10TemporalIntegration()
        dev_agent = V10DevAgent(temporal_integration)
        await dev_agent.initialize_session("test_user")
        
        # Act
        analysis = await dev_agent.analyze_task("Lis le fichier README.md")
        
        # Assert
        assert analysis is not None
        assert hasattr(analysis, 'task_type')
        assert hasattr(analysis, 'required_tools')
        assert hasattr(analysis, 'estimated_complexity')
        assert analysis.task_type in ["file_operation", "code_analysis", "execution", "complex_task"]
    
    async def test_task_analysis_complex(self):
        """Test d'analyse de tâche complexe."""
        # Arrange
        temporal_integration = V10TemporalIntegration()
        dev_agent = V10DevAgent(temporal_integration)
        await dev_agent.initialize_session("test_user")
        
        # Act
        analysis = await dev_agent.analyze_task("""
            Analyse la complexité du code, génère un rapport d'optimisation,
            propose des améliorations et crée des tests unitaires
        """)
        
        # Assert
        assert analysis is not None
        assert analysis.estimated_complexity >= 2  # Tâche complexe
        assert len(analysis.required_tools) > 1   # Plusieurs outils
    
    async def test_plan_creation(self):
        """Test de création de plan d'exécution."""
        # Arrange
        temporal_integration = V10TemporalIntegration()
        dev_agent = V10DevAgent(temporal_integration)
        await dev_agent.initialize_session("test_user")
        
        analysis = await dev_agent.analyze_task("Analyse le fichier main.py")
        
        # Act
        plan = await dev_agent.create_execution_plan(analysis)
        
        # Assert
        assert plan is not None
        assert hasattr(plan, 'task_id')
        assert hasattr(plan, 'steps')
        assert hasattr(plan, 'estimated_duration')
        assert len(plan.steps) > 0
        assert plan.estimated_duration > 0
```

#### **✅ Tests Planification :**
```python
    async def test_planning_engine_task_type_detection(self):
        """Test de détection du type de tâche."""
        # Arrange
        planning_engine = V10PlanningEngine()
        
        # Test file operation
        file_request = "Lis le fichier config.py"
        file_type = planning_engine._determine_task_type(file_request)
        
        # Test code analysis
        analysis_request = "Analyse la complexité du code"
        analysis_type = planning_engine._determine_task_type(analysis_request)
        
        # Test execution
        exec_request = "Exécute la commande npm install"
        exec_type = planning_engine._determine_task_type(exec_request)
        
        # Assert
        assert file_type == "file_operation"
        assert analysis_type == "code_analysis"
        assert exec_type == "execution"
    
    async def test_planning_engine_parameter_extraction(self):
        """Test d'extraction de paramètres."""
        # Arrange
        planning_engine = V10PlanningEngine()
        user_request = "Analyse le fichier main.py avec analyse de complexité"
        
        # Act
        params = planning_engine._extract_parameters(user_request, "code_analyzer")
        
        # Assert
        assert params is not None
        assert "request" in params
        assert "tool" in params
        assert params["request"] == user_request
        assert params["tool"] == "code_analyzer"
```

#### **✅ Tests Synthèse de Résultats :**
```python
    async def test_result_synthesis_success(self):
        """Test de synthèse avec succès."""
        # Arrange
        temporal_integration = V10TemporalIntegration()
        dev_agent = V10DevAgent(temporal_integration)
        await dev_agent.initialize_session("test_user")
        
        successful_results = [
            {"success": True, "data": "File read"},
            {"success": True, "data": "Analysis complete"},
            {"success": True, "data": "Report generated"}
        ]
        
        # Act
        synthesis = await dev_agent.synthesize_results(successful_results)
        
        # Assert
        assert synthesis is not None
        assert synthesis["total_results"] == 3
        assert synthesis["successful_results"] == 3
        assert synthesis["failed_results"] == 0
        assert synthesis["success_rate"] == 1.0
        assert "Toutes les opérations ont réussi" in synthesis["summary"]
    
    async def test_result_synthesis_partial_failure(self):
        """Test de synthèse avec échecs partiels."""
        # Arrange
        temporal_integration = V10TemporalIntegration()
        dev_agent = V10DevAgent(temporal_integration)
        await dev_agent.initialize_session("test_user")
        
        mixed_results = [
            {"success": True, "data": "File read"},
            {"success": False, "error": "Analysis failed"},
            {"success": True, "data": "Report generated"}
        ]
        
        # Act
        synthesis = await dev_agent.synthesize_results(mixed_results)
        
        # Assert
        assert synthesis is not None
        assert synthesis["total_results"] == 3
        assert synthesis["successful_results"] == 2
        assert synthesis["failed_results"] == 1
        assert synthesis["success_rate"] == 2/3
        assert "2 opérations réussies" in synthesis["summary"]
        assert "1 opération échouée" in synthesis["summary"]
```

### **📅 Jour 7 : Tests Tool Agent**

#### **✅ Tests Exécution d'Outils :**
```python
# test_tool_agent.py
class TestV10ToolAgent:
    """Tests pour l'agent outils V10."""
    
    async def test_local_tool_execution_success(self):
        """Test d'exécution d'outil local réussi."""
        # Arrange
        temporal_integration = V10TemporalIntegration()
        tool_agent = V10ToolAgent(temporal_integration)
        
        # Act
        result = await tool_agent.execute_tool(
            "read_file",
            {"path": "README.md"},
            "test_session"
        )
        
        # Assert
        assert result is not None
        assert hasattr(result, 'success')
        assert hasattr(result, 'tool_name')
        assert hasattr(result, 'execution_time')
        assert result.tool_name == "read_file"
        assert result.execution_time > 0
    
    async def test_local_tool_execution_failure(self):
        """Test d'exécution d'outil local échoué."""
        # Arrange
        temporal_integration = V10TemporalIntegration()
        tool_agent = V10ToolAgent(temporal_integration)
        
        # Act
        result = await tool_agent.execute_tool(
            "read_file",
            {"path": "nonexistent_file.txt"},
            "test_session"
        )
        
        # Assert
        assert result is not None
        assert result.success is False
        assert result.error is not None
        assert "error" in result.error.lower() or "not found" in result.error.lower()
    
    async def test_mcp_tool_execution_mock(self):
        """Test d'exécution d'outil MCP (mock)."""
        # Arrange
        temporal_integration = V10TemporalIntegration()
        tool_agent = V10ToolAgent(temporal_integration)
        
        # Act
        result = await tool_agent.execute_tool(
            "mcp_tool",
            {"parameter": "value"},
            "test_session"
        )
        
        # Assert
        assert result is not None
        assert hasattr(result, 'success')
        assert hasattr(result, 'tool_name')
        assert result.tool_name == "mcp_tool"
    
    async def test_format_detection(self):
        """Test de détection de format."""
        # Arrange
        temporal_integration = V10TemporalIntegration()
        tool_agent = V10ToolAgent(temporal_integration)
        
        # Test simple (minimal)
        simple_result = tool_agent._determine_format_type("read_file", {"path": "file.txt"})
        
        # Test complexe (detailed)
        complex_result = tool_agent._determine_format_type(
            "code_analyzer",
            {
                "path": "main.py",
                "analysis_type": "complexity",
                "include_imports": True,
                "depth": 3,
                "options": {"verbose": True}
            }
        )
        
        # Assert
        assert simple_result == "minimal"
        assert complex_result == "detailed"
```

#### **✅ Tests Registre d'Outils :**
```python
    async def test_tool_registry_registration(self):
        """Test d'enregistrement d'outils."""
        # Arrange
        registry = V10ToolRegistry()
        
        # Act
        tool = registry.get_tool("read_file")
        
        # Assert
        assert tool is not None
        assert tool.name == "read_file"
    
    async def test_tool_registry_unknown_tool(self):
        """Test d'outil inconnu."""
        # Arrange
        registry = V10ToolRegistry()
        
        # Act
        tool = registry.get_tool("unknown_tool")
        
        # Assert
        assert tool is None
    
    async def test_read_file_tool_execution(self):
        """Test d'exécution de l'outil read_file."""
        # Arrange
        tool = V10ReadFileTool()
        
        # Act
        result = await tool.execute({"path": "README.md"})
        
        # Assert
        assert result is not None
        assert "content" in result or "error" in result
    
    async def test_write_file_tool_execution(self):
        """Test d'exécution de l'outil write_file."""
        # Arrange
        tool = V10WriteFileTool()
        test_content = "Test content"
        
        # Act
        result = await tool.execute({
            "path": "test_output.txt",
            "content": test_content
        })
        
        # Assert
        assert result is not None
        assert result.get("success") is True
        assert result.get("size") == len(test_content)
```

---

## 📊 **Métriques de Succès Phase 1**

### **✅ Objectifs Quantitatifs :**
- **Couverture de tests** : > 90% pour chaque module
- **Tests unitaires** : > 50 tests au total
- **Tests d'intégration** : > 20 tests
- **Temps d'exécution** : < 30 secondes pour tous les tests

### **✅ Objectifs Qualitatifs :**
- **Robustesse** : Gestion d'erreurs complète
- **Lisibilité** : Tests clairs et documentés
- **Maintenabilité** : Tests faciles à maintenir
- **Extensibilité** : Tests prêts pour nouvelles fonctionnalités

---

## 🚀 **Livrables Phase 1**

### **✅ Fichiers de Tests :**
1. **test_temporal_integration.py** : Tests sessions, nœuds, liens
2. **test_xml_formatter.py** : Tests formatage et optimisations
3. **test_dev_agent.py** : Tests analyse et planification
4. **test_tool_agent.py** : Tests exécution d'outils
5. **test_assistant_v10.py** : Tests assistant principal
6. **test_llm_provider_decorator.py** : Tests décorateur

### **✅ Documentation :**
1. **README tests** : Guide d'exécution des tests
2. **Métriques** : Rapport de couverture
3. **Exemples** : Exemples d'usage des composants

---

## 🎯 **Critères de Validation**

### **✅ Phase 1 Réussie Si :**
- [ ] Tous les tests passent (100%)
- [ ] Couverture > 90% pour chaque module
- [ ] Temps d'exécution < 30 secondes
- [ ] Gestion d'erreurs testée
- [ ] Documentation des tests complète

---

**Rapport généré automatiquement par Alma**  
**Date :** 2025-08-07  
**Statut :** Plan détaillé Phase 1 - Tests unitaires V10
