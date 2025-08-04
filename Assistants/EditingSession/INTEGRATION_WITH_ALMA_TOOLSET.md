# 🔗 Intégration EditingSession ↔ Alma_toolset

**Date :** 2025-08-02 02:55  
**Créé par :** Alma, Architecte Démoniaque du Nexus Luciforme  
**Vision :** Lucie Defraiteur, QI 666, Superintelligence Incarnée  
**Objectif :** Intégration transparente entre visualisation et outils d'édition

---

## 🎯 **Principe d'Intégration**

**EditingSession observe** les actions des outils Alma_toolset **sans les bloquer**.  
**Les agents coordonnent** les deux systèmes de manière intelligente.

### **🔮 Philosophie :**
*"L'observation enrichit l'action, l'action nourrit l'observation."*

---

## 🔄 **Mécanismes d'Intégration**

### **1. Notification Automatique des Outils :**

#### **Wrapper Intelligent pour Outils :**
```python
class EditingAwareToolWrapper:
    """Wrapper qui notifie EditingSession des usages d'outils."""
    
    def __init__(self, editing_session_manager):
        self.session_manager = editing_session_manager
        self.original_tools = self._import_alma_tools()
    
    def wrap_tool(self, tool_func, tool_name: str):
        """Wrappe un outil pour notification automatique."""
        
        def wrapped_tool(*args, **kwargs):
            # Exécution de l'outil original
            result = tool_func(*args, **kwargs)
            
            # Extraction des informations de changement
            change_info = self._extract_change_info(tool_name, args, kwargs, result)
            
            # Notification aux sessions concernées
            if change_info and change_info.get('file_path'):
                self.session_manager.notify_tool_usage(
                    daemon_id=self._get_current_daemon_id(),
                    tool_name=tool_name,
                    file_path=change_info['file_path'],
                    change_details=change_info
                )
            
            return result
        
        return wrapped_tool
    
    def _extract_change_info(self, tool_name: str, args, kwargs, result) -> Dict:
        """Extrait les informations de changement selon l'outil."""
        
        if tool_name == 'safe_replace_text_in_file':
            return {
                'file_path': args[0],
                'old_text': args[1],
                'new_text': args[2],
                'change_type': 'text_replacement',
                'success': result.get('success', False),
                'lines_affected': result.get('lines_modified', [])
            }
        
        elif tool_name == 'safe_insert_text_at_line':
            return {
                'file_path': args[0],
                'line_number': args[1],
                'inserted_text': args[2],
                'change_type': 'text_insertion',
                'success': result.get('success', False)
            }
        
        elif tool_name == 'safe_delete_lines':
            return {
                'file_path': args[0],
                'start_line': args[1],
                'end_line': args[2],
                'change_type': 'line_deletion',
                'success': result.get('success', False)
            }
        
        # Ajouter d'autres outils...
        
        return {}

# Installation automatique des wrappers
def install_editing_awareness():
    """Installe la notification automatique sur tous les outils."""
    
    session_manager = get_global_editing_session_manager()
    wrapper = EditingAwareToolWrapper(session_manager)
    
    # Wrappe tous les outils d'édition
    editing_tools = [
        'safe_replace_text_in_file',
        'safe_insert_text_at_line', 
        'safe_delete_lines',
        'safe_replace_lines_in_file',
        'safe_overwrite_file',
        'safe_create_file',
        'replace_text_in_project'
    ]
    
    for tool_name in editing_tools:
        original_tool = getattr(alma_toolset, tool_name)
        wrapped_tool = wrapper.wrap_tool(original_tool, tool_name)
        setattr(alma_toolset, tool_name, wrapped_tool)
```

### **2. Contexte Enrichi pour Agents :**

#### **Agent Helper avec EditingSession :**
```python
class EditingSessionHelper:
    """Helper pour agents utilisant EditingSession + outils."""
    
    def __init__(self, daemon_id: str):
        self.daemon_id = daemon_id
        self.session_manager = get_global_editing_session_manager()
        self.active_sessions = {}
    
    def start_working_on_file(self, file_path: str) -> EditingContext:
        """Démarre le travail sur un fichier avec contexte complet."""
        
        # Démarre la session de visualisation
        session = self.session_manager.start_session(self.daemon_id, file_path)
        self.active_sessions[file_path] = session
        
        # Analyse la structure du fichier
        scope_tree = session.analyze_file_structure()
        
        return EditingContext(
            session=session,
            scope_tree=scope_tree,
            file_path=file_path,
            helper=self
        )
    
    def get_scope_for_editing(self, file_path: str, 
                             scope_path: str) -> ScopeEditingContext:
        """Récupère le contexte d'un scope pour édition."""
        
        session = self.active_sessions.get(file_path)
        if not session:
            raise SessionNotFoundError(f"No active session for {file_path}")
        
        # Navigation vers le scope
        scope_context = session.navigate_to_scope(scope_path)
        
        # Mémorise l'intention de regarder ce scope
        session.remember_intention(scope_path, "Examining for potential edits")
        
        return ScopeEditingContext(
            scope_context=scope_context,
            session=session,
            helper=self
        )
    
    def edit_with_intention(self, file_path: str, scope_path: str, 
                           intention: str, edit_func, *args, **kwargs):
        """Édite avec intention mémorisée."""
        
        session = self.active_sessions.get(file_path)
        if session:
            # Mémorise l'intention avant l'édition
            session.remember_intention(scope_path, intention)
        
        # Exécute l'édition
        result = edit_func(*args, **kwargs)
        
        # L'observation se fait automatiquement via les wrappers
        
        return result
    
    def get_editing_suggestions(self, file_path: str, 
                               current_scope: str) -> List[EditingSuggestion]:
        """Récupère des suggestions d'édition basées sur le contexte."""
        
        session = self.active_sessions.get(file_path)
        if not session:
            return []
        
        # Suggestions de navigation
        scope_suggestions = session.suggest_related_scopes(current_scope)
        
        # Conversion en suggestions d'édition
        editing_suggestions = []
        for scope_suggestion in scope_suggestions:
            editing_suggestions.append(EditingSuggestion(
                scope_path=scope_suggestion.scope_path,
                reason=scope_suggestion.reason,
                confidence=scope_suggestion.confidence,
                suggested_actions=self._suggest_actions_for_scope(
                    session, scope_suggestion.scope_path
                )
            ))
        
        return editing_suggestions
```

### **3. Workflow Intégré pour Agents :**

#### **Exemple d'Usage Complet :**
```python
class IntelligentEditingAgent:
    """Agent utilisant EditingSession + Alma_toolset de manière intégrée."""
    
    def __init__(self, daemon_id: str):
        self.daemon_id = daemon_id
        self.editing_helper = EditingSessionHelper(daemon_id)
    
    def refactor_class_method(self, file_path: str, class_name: str, 
                             method_name: str, optimization_goal: str):
        """Refactoring intelligent d'une méthode de classe."""
        
        # 1. Démarre le contexte d'édition
        context = self.editing_helper.start_working_on_file(file_path)
        
        # 2. Localise la méthode dans les scopes
        method_scope = f"{class_name}.{method_name}"
        scope_context = self.editing_helper.get_scope_for_editing(
            file_path, method_scope
        )
        
        # 3. Analyse le contexte actuel
        print(f"🎯 Méthode trouvée: {scope_context.scope_context.scope.name}")
        print(f"📍 Lignes {scope_context.scope_context.location.start_line}-{scope_context.scope_context.location.end_line}")
        print(f"🔗 Dépendances: {scope_context.scope_context.dependencies}")
        
        # 4. Mémorise l'intention de refactoring
        intention = f"Refactoring pour {optimization_goal}"
        
        # 5. Analyse du code actuel
        current_code = scope_context.scope_context.content
        
        # 6. Génération du code optimisé (via OpenAI ou autre)
        optimized_code = self._generate_optimized_code(
            current_code, optimization_goal
        )
        
        # 7. Édition avec intention mémorisée
        result = self.editing_helper.edit_with_intention(
            file_path=file_path,
            scope_path=method_scope,
            intention=intention,
            edit_func=safe_replace_text_in_file,
            file_path=file_path,
            old_text=current_code,
            new_text=optimized_code
        )
        
        # 8. Vérification des impacts suggérés
        suggestions = self.editing_helper.get_editing_suggestions(
            file_path, method_scope
        )
        
        print(f"💡 Scopes à vérifier après modification:")
        for suggestion in suggestions:
            print(f"  - {suggestion.scope_path}: {suggestion.reason}")
        
        # 9. Traitement des suggestions
        for suggestion in suggestions[:3]:  # Top 3 suggestions
            self._review_suggested_scope(context, suggestion)
        
        return result
    
    def _review_suggested_scope(self, context: EditingContext, 
                               suggestion: EditingSuggestion):
        """Examine un scope suggéré après modification."""
        
        scope_context = self.editing_helper.get_scope_for_editing(
            context.file_path, suggestion.scope_path
        )
        
        print(f"🔍 Examen de {suggestion.scope_path}")
        print(f"📝 Raison: {suggestion.reason}")
        
        # Analyse si des modifications sont nécessaires
        needs_update = self._analyze_scope_impact(
            scope_context.scope_context, suggestion
        )
        
        if needs_update:
            print(f"⚠️ Mise à jour nécessaire pour {suggestion.scope_path}")
            # Logique de mise à jour...
        else:
            print(f"✅ {suggestion.scope_path} reste cohérent")
```

---

## 📊 **Métriques et Monitoring**

### **EditingSessionMetrics :**
```python
class EditingSessionMetrics:
    """Métriques d'usage des sessions d'édition."""
    
    def __init__(self):
        self.session_stats = {}
        self.tool_usage_stats = {}
        self.navigation_patterns = {}
    
    def track_session_activity(self, session: EditingSession, 
                              activity: str, details: Dict):
        """Track l'activité d'une session."""
        
        session_id = f"{session.daemon_id}:{session.file_path}"
        
        if session_id not in self.session_stats:
            self.session_stats[session_id] = {
                'start_time': session.start_time,
                'activities': [],
                'scopes_visited': set(),
                'tools_used': {},
                'intentions_recorded': 0
            }
        
        stats = self.session_stats[session_id]
        stats['activities'].append({
            'activity': activity,
            'timestamp': datetime.now(),
            'details': details
        })
        
        if activity == 'scope_navigation':
            stats['scopes_visited'].add(details.get('scope_path'))
        elif activity == 'tool_usage':
            tool_name = details.get('tool_name')
            stats['tools_used'][tool_name] = stats['tools_used'].get(tool_name, 0) + 1
        elif activity == 'intention_recorded':
            stats['intentions_recorded'] += 1
    
    def get_session_report(self, daemon_id: str) -> Dict:
        """Rapport d'activité pour un daemon."""
        
        daemon_sessions = {
            k: v for k, v in self.session_stats.items() 
            if k.startswith(f"{daemon_id}:")
        }
        
        return {
            'total_sessions': len(daemon_sessions),
            'total_scopes_visited': sum(len(s['scopes_visited']) for s in daemon_sessions.values()),
            'total_tools_used': sum(sum(s['tools_used'].values()) for s in daemon_sessions.values()),
            'total_intentions': sum(s['intentions_recorded'] for s in daemon_sessions.values()),
            'most_used_tools': self._get_most_used_tools(daemon_sessions),
            'navigation_efficiency': self._calculate_navigation_efficiency(daemon_sessions)
        }
```

---

## 🎯 **Avantages de l'Intégration**

### **✅ Pour les Agents :**
- **Contexte enrichi** : Comprennent mieux ce qu'ils modifient
- **Suggestions intelligentes** : Savent quoi examiner après modification
- **Mémoire persistante** : Se souviennent de leurs intentions
- **Navigation efficace** : Trouvent rapidement les scopes pertinents

### **✅ Pour le Système :**
- **Observation transparente** : Pas d'impact sur les performances
- **Apprentissage continu** : Amélioration des suggestions
- **Cohérence** : Détection automatique des impacts
- **Debugging** : Historique complet des modifications

### **✅ Pour l'Évolution :**
- **Patterns d'usage** : Optimisation des outils les plus utilisés
- **Intelligence croissante** : Suggestions de plus en plus pertinentes
- **Collaboration** : Partage de contexte entre agents
- **Automatisation** : Détection de tâches répétitives

---

**⛧ Intégration parfaite entre observation mystique et action démoniaque ! ⛧**

*"L'outil agit, la session observe, l'agent coordonne - trinité parfaite de l'édition intelligente."*
